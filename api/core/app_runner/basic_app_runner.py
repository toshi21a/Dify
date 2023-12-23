import logging
import time
from typing import cast, Optional, Tuple, List, Union, Generator


from core.callback_handler.index_tool_callback_handler import DatasetIndexToolCallbackHandler
from core.entities.application_entities import ApplicationGenerateEntity, PromptTemplateEntity, ModelConfigEntity, \
    AppOrchestrationConfigEntity, InvokeFrom, ExternalDataVariableEntity, DatasetEntity
from core.application_queue_manager import ApplicationQueueManager
from core.features.annotation_reply import AnnotationReplyFeature
from core.features.dataset_retrieval import DatasetRetrievalReply
from core.features.external_data_fetch import ExternalDataFetchFeature
from core.features.hosting_moderation import HostingModerationFeature
from core.features.moderation import ModerationFeature
from core.file.file_obj import FileObj
from core.memory.token_buffer_memory import TokenBufferMemory
from core.model_runtime.entities.llm_entities import LLMResult, LLMUsage, LLMResultChunk, LLMResultChunkDelta
from core.model_runtime.entities.message_entities import AssistantPromptMessage, PromptMessage
from core.model_runtime.entities.model_entities import ModelPropertyKey
from core.model_runtime.errors.invoke import InvokeBadRequestError
from core.model_runtime.model_providers.__base.large_language_model import LargeLanguageModel
from core.moderation.base import ModerationException
from core.prompt.prompt_transform import PromptTransform
from extensions.ext_database import db
from models.model import Conversation, Message, App

logger = logging.getLogger(__name__)


class BasicApplicationRunner:
    """
    Basic Application Runner
    """

    def run(self, application_generate_entity: ApplicationGenerateEntity,
            queue_manager: ApplicationQueueManager,
            conversation: Conversation,
            message: Message) -> None:
        """
        Run application
        :param application_generate_entity: application generate entity
        :param queue_manager: application queue manager
        :param conversation: conversation
        :param message: message
        :return:
        """
        app_record = db.session.query(App).filter(App.id == application_generate_entity.app_id).first()
        if not app_record:
            raise ValueError(f"App not found")

        app_orchestration_config = application_generate_entity.app_orchestration_config_entity

        inputs = application_generate_entity.inputs
        query = application_generate_entity.query
        files = application_generate_entity.files

        # Pre-calculate the number of tokens of the prompt messages,
        # and return the rest number of tokens by model context token size limit and max token size limit.
        # If the rest number of tokens is not enough, raise exception.
        # Include: prompt template, inputs, query(optional), files(optional)
        # Not Include: memory, external data, dataset context
        self.get_pre_calculate_rest_tokens(
            app_record=app_record,
            model_config=app_orchestration_config.model_config,
            prompt_template_entity=app_orchestration_config.prompt_template,
            inputs=inputs,
            files=files,
            query=query
        )

        memory = None
        if application_generate_entity.conversation_id:
            # get memory of conversation (read-only)
            memory = TokenBufferMemory(
                conversation=conversation,
                model_config=app_orchestration_config.model_config
            )

        # organize all inputs and template to prompt messages
        # Include: prompt template, inputs, query(optional), files(optional)
        #          memory(optional)
        prompt_messages, stop = self.originze_prompt_messages(
            app_record=app_record,
            model_config=app_orchestration_config.model_config,
            prompt_template_entity=app_orchestration_config.prompt_template,
            inputs=inputs,
            files=files,
            query=query,
            memory=memory
        )

        # moderation
        try:
            # process sensitive_word_avoidance
            _, inputs, query = self.moderation_for_inputs(
                app_id=app_record.id,
                tenant_id=application_generate_entity.tenant_id,
                app_orchestration_config_entity=app_orchestration_config,
                inputs=inputs,
                query=query,
            )
        except ModerationException as e:
            self.direct_output(
                queue_manager=queue_manager,
                app_orchestration_config=app_orchestration_config,
                prompt_messages=prompt_messages,
                text=str(e),
                stream=application_generate_entity.stream
            )
            return

        if query:
            # annotation reply
            annotation_reply = self.query_app_annotations_to_reply(
                queue_manager=queue_manager,
                model_config=app_orchestration_config.model_config,
                app_record=app_record,
                message=message,
                query=query,
                user_id=application_generate_entity.user_id,
                invoke_from=application_generate_entity.invoke_from
            )

            if annotation_reply:
                return

            # fill in variable inputs from external data tools if exists
            external_data_tools = app_orchestration_config.external_data_variables
            if external_data_tools:
                inputs = self.fill_in_inputs_from_external_data_tools(
                    tenant_id=app_record.tenant_id,
                    app_id=app_record.id,
                    external_data_tools=external_data_tools,
                    inputs=inputs,
                    query=query
                )

        # get context from datasets
        context = None
        if app_orchestration_config.dataset:
            context = self.retrieve_dataset_context(
                tenant_id=app_record.tenant_id,
                queue_manager=queue_manager,
                model_config=app_orchestration_config.model_config,
                dataset_config=app_orchestration_config.dataset,
                message=message,
                inputs=inputs,
                query=query,
                user_id=application_generate_entity.user_id,
                invoke_from=application_generate_entity.invoke_from
            )

        # reorganize all inputs and template to prompt messages
        # Include: prompt template, inputs, query(optional), files(optional)
        #          memory(optional), external data, dataset context(optional)
        prompt_messages, stop = self.originze_prompt_messages(
            app_record=app_record,
            model_config=app_orchestration_config.model_config,
            prompt_template_entity=app_orchestration_config.prompt_template,
            inputs=inputs,
            files=files,
            query=query,
            context=context,
            memory=memory
        )

        # check hosting moderation
        hosting_moderation_result = self.check_hosting_moderation(
            application_generate_entity=application_generate_entity,
            queue_manager=queue_manager,
            prompt_messages=prompt_messages
        )

        if hosting_moderation_result:
            return

        # Re-calculate the max tokens if sum(prompt_token +  max_tokens) over model token limit
        self.recale_llm_max_tokens(
            model_config=app_orchestration_config.model_config,
            prompt_messages=prompt_messages
        )

        # Invoke model
        model_instance = app_orchestration_config.model_config.provider_model_bundle.model_instance
        model_instance = cast(LargeLanguageModel, model_instance)

        invoke_result = model_instance.invoke(
            model=app_orchestration_config.model_config.model,
            credentials=app_orchestration_config.model_config.credentials,
            prompt_messages=prompt_messages,
            model_parameters=app_orchestration_config.model_config.parameters,
            stop=stop,
            stream=application_generate_entity.stream,
            user=application_generate_entity.user_id,
        )

        # handle invoke result
        self._handle_invoke_result(
            invoke_result=invoke_result,
            queue_manager=queue_manager,
            stream=application_generate_entity.stream
        )

    def _handle_invoke_result(self, invoke_result: Union[LLMResult, Generator],
                              queue_manager: ApplicationQueueManager,
                              stream: bool) -> None:
        """
        Handle invoke result
        :param invoke_result: invoke result
        :param queue_manager: application queue manager
        :param app_orchestration_config: app orchestration config
        :param prompt_messages: prompt messages
        :param stream: stream
        :return:
        """
        if not stream:
            self._handle_invoke_result_direct(
                invoke_result=invoke_result,
                queue_manager=queue_manager
            )
        else:
            self._handle_invoke_result_stream(
                invoke_result=invoke_result,
                queue_manager=queue_manager
            )

    def _handle_invoke_result_direct(self, invoke_result: LLMResult,
                                     queue_manager: ApplicationQueueManager) -> None:
        """
        Handle invoke result direct
        :param invoke_result: invoke result
        :param queue_manager: application queue manager
        :return:
        """
        queue_manager.publish_message_end(
            llm_result=invoke_result
        )

    def _handle_invoke_result_stream(self, invoke_result: Generator,
                                     queue_manager: ApplicationQueueManager) -> None:
        """
        Handle invoke result
        :param invoke_result: invoke result
        :param queue_manager: application queue manager
        :return:
        """
        model = None
        prompt_messages = []
        text = ''
        usage = None
        for result in invoke_result:
            queue_manager.publish_chunk_message(result)

            text += result.message.content

            if not model:
                model = result.model

            if not prompt_messages:
                prompt_messages = result.prompt_messages

            if not usage and result.delta.usage:
                usage = result.delta.usage

        llm_result = LLMResult(
            model=model,
            prompt_messages=prompt_messages,
            message=AssistantPromptMessage(content=text),
            usage=usage
        )

        queue_manager.publish_message_end(
            llm_result=llm_result
        )

    def originze_prompt_messages(self, app_record: App,
                                 model_config: ModelConfigEntity,
                                 prompt_template_entity: PromptTemplateEntity,
                                 inputs: dict[str, str],
                                 files: list[FileObj],
                                 query: Optional[str] = None,
                                 context: Optional[str] = None,
                                 memory: Optional[TokenBufferMemory] = None) \
            -> Tuple[List[PromptMessage], Optional[List[str]]]:
        """
        Organize prompt messages
        :param context:
        :param app_record: app record
        :param model_config: model config entity
        :param prompt_template_entity: prompt template entity
        :param inputs: inputs
        :param files: files
        :param query: query
        :param memory: memory
        :return:
        """
        prompt_transform = PromptTransform()

        # get prompt without memory and context
        if prompt_template_entity.prompt_type == PromptTemplateEntity.PromptType.SIMPLE:
            prompt_messages, stop = prompt_transform.get_prompt(
                app_mode=app_record.mode,
                prompt_template_entity=prompt_template_entity,
                inputs=inputs,
                query=query if query else '',
                files=files,
                context=context,
                memory=memory,
                model_config=model_config
            )
        else:
            prompt_messages = prompt_transform.get_advanced_prompt(
                app_mode=app_record.mode,
                prompt_template_entity=prompt_template_entity,
                inputs=inputs,
                query=query,
                files=files,
                context=context,
                memory=memory,
                model_config=model_config
            )
            stop = model_config.stop

        return prompt_messages, stop

    def get_pre_calculate_rest_tokens(self, app_record: App,
                                      model_config: ModelConfigEntity,
                                      prompt_template_entity: PromptTemplateEntity,
                                      inputs: dict[str, str],
                                      files: list[FileObj],
                                      query: Optional[str] = None) -> int:
        """
        Get pre calculate rest tokens
        :param app_record: app record
        :param model_config: model config entity
        :param prompt_template_entity: prompt template entity
        :param inputs: inputs
        :param files: files
        :param query: query
        :return:
        """
        model_instance = model_config.provider_model_bundle.model_instance
        model_instance = cast(LargeLanguageModel, model_instance)

        model_context_tokens = model_config.model_schema.model_properties.get(ModelPropertyKey.CONTEXT_SIZE)

        max_tokens = 0
        for parameter_rule in model_config.model_schema.parameter_rules:
            if (parameter_rule.name == 'max_tokens'
                    or (parameter_rule.use_template and parameter_rule.use_template == 'max_tokens')):
                max_tokens = (model_config.parameters.get(parameter_rule.name)
                              or model_config.parameters.get(parameter_rule.use_template))

        if model_context_tokens is None:
            return -1

        if max_tokens is None:
            max_tokens = 0

        # get prompt messages without memory and context
        prompt_messages, stop = self.originze_prompt_messages(
            app_record=app_record,
            model_config=model_config,
            prompt_template_entity=prompt_template_entity,
            inputs=inputs,
            files=files,
            query=query
        )

        prompt_tokens = model_instance.get_num_tokens(
            model_config.model,
            prompt_messages
        )

        rest_tokens = model_context_tokens - max_tokens - prompt_tokens
        if rest_tokens < 0:
            raise InvokeBadRequestError("Query or prefix prompt is too long, you can reduce the prefix prompt, "
                                        "or shrink the max token, or switch to a llm with a larger token limit size.")

        return rest_tokens

    def moderation_for_inputs(self, app_id: str,
                              tenant_id: str,
                              app_orchestration_config_entity: AppOrchestrationConfigEntity,
                              inputs: dict,
                              query: str) -> Tuple[bool, dict, str]:
        """
        Process sensitive_word_avoidance.
        :param app_id: app id
        :param tenant_id: tenant id
        :param app_orchestration_config_entity: app orchestration config entity
        :param inputs: inputs
        :param query: query
        :return:
        """
        moderation_feature = ModerationFeature()
        return moderation_feature.check(
            app_id=app_id,
            tenant_id=tenant_id,
            app_orchestration_config_entity=app_orchestration_config_entity,
            inputs=inputs,
            query=query,
        )

    def query_app_annotations_to_reply(self, queue_manager: ApplicationQueueManager,
                                       model_config: ModelConfigEntity,
                                       app_record: App,
                                       message: Message,
                                       query: str,
                                       user_id: str,
                                       invoke_from: InvokeFrom) -> bool:
        """
        Query app annotations to reply
        :param queue_manager: queue manager
        :param model_config: model config entity
        :param app_record: app record
        :param message: message
        :param query: query
        :param user_id: user id
        :param invoke_from: invoke from
        :return:
        """
        annotation_reply_feature = AnnotationReplyFeature()
        return annotation_reply_feature.query(
            queue_manager=queue_manager,
            model_config=model_config,
            app_record=app_record,
            message=message,
            query=query,
            user_id=user_id,
            invoke_from=invoke_from
        )

    def fill_in_inputs_from_external_data_tools(self, tenant_id: str,
                                                app_id: str,
                                                external_data_tools: list[ExternalDataVariableEntity],
                                                inputs: dict,
                                                query: str) -> dict:
        """
        Fill in variable inputs from external data tools if exists.

        :param tenant_id: workspace id
        :param app_id: app id
        :param external_data_tools: external data tools configs
        :param inputs: the inputs
        :param query: the query
        :return: the filled inputs
        """
        external_data_fetch_feature = ExternalDataFetchFeature()
        return external_data_fetch_feature.fetch(
            tenant_id=tenant_id,
            app_id=app_id,
            external_data_tools=external_data_tools,
            inputs=inputs,
            query=query
        )

    def retrieve_dataset_context(self, tenant_id: str,
                                 queue_manager: ApplicationQueueManager,
                                 model_config: ModelConfigEntity,
                                 dataset_config: DatasetEntity,
                                 message: Message,
                                 inputs: dict,
                                 query: str,
                                 user_id: str,
                                 invoke_from: InvokeFrom) -> str:
        """
        Retrieve dataset context
        :param tenant_id: tenant id
        :param queue_manager: queue manager
        :param model_config: model config
        :param dataset_config: dataset config
        :param message: message
        :param inputs: inputs
        :param query: query
        :param user_id: user id
        :param invoke_from: invoke from
        :return:
        """
        hit_callback = DatasetIndexToolCallbackHandler(queue_manager, message.id, user_id)

        if model_config.mode == 'completion':
            query = inputs.get(dataset_config.retrieve_config, "")

        dataset_retrieval = DatasetRetrievalReply()
        return dataset_retrieval.retrieve(
            tenant_id=tenant_id,
            model_config=model_config,
            config=dataset_config,
            query=query,
            invoke_from=invoke_from,
            hit_callback=hit_callback
        )

    def recale_llm_max_tokens(self, model_config: ModelConfigEntity,
                              prompt_messages: List[PromptMessage]):
        # recalc max_tokens if sum(prompt_token +  max_tokens) over model token limit
        model_instance = model_config.provider_model_bundle.model_instance
        model_instance = cast(LargeLanguageModel, model_instance)

        model_context_tokens = model_config.model_schema.model_properties.get(ModelPropertyKey.CONTEXT_SIZE)

        max_tokens = 0
        for parameter_rule in model_config.model_schema.parameter_rules:
            if (parameter_rule.name == 'max_tokens'
                    or (parameter_rule.use_template and parameter_rule.use_template == 'max_tokens')):
                max_tokens = (model_config.parameters.get(parameter_rule.name)
                              or model_config.parameters.get(parameter_rule.use_template))

        if model_context_tokens is None:
            return -1

        if max_tokens is None:
            max_tokens = 0

        prompt_tokens = model_instance.get_num_tokens(
            model_config.model,
            prompt_messages
        )

        if prompt_tokens + max_tokens > model_context_tokens:
            max_tokens = max(model_context_tokens - prompt_tokens, 16)

            for parameter_rule in model_config.model_schema.parameter_rules:
                if (parameter_rule.name == 'max_tokens'
                        or (parameter_rule.use_template and parameter_rule.use_template == 'max_tokens')):
                    model_config.parameters[parameter_rule.name] = max_tokens

    def check_hosting_moderation(self, application_generate_entity: ApplicationGenerateEntity,
                                 queue_manager: ApplicationQueueManager,
                                 prompt_messages: list[PromptMessage]) -> bool:
        """
        Check hosting moderation
        :param application_generate_entity: application generate entity
        :param queue_manager: queue manager
        :param prompt_messages: prompt messages
        :return:
        """
        hosting_moderation_feature = HostingModerationFeature()
        moderation_result = hosting_moderation_feature.check(
            application_generate_entity=application_generate_entity,
            prompt_messages=prompt_messages
        )

        if moderation_result:
            self.direct_output(
                queue_manager=queue_manager,
                app_orchestration_config=application_generate_entity.app_orchestration_config_entity,
                prompt_messages=prompt_messages,
                text="I apologize for any confusion, " \
                     "but I'm an AI assistant to be helpful, harmless, and honest.",
                stream=application_generate_entity.stream
            )

        return moderation_result

    def direct_output(self, queue_manager: ApplicationQueueManager,
                      app_orchestration_config: AppOrchestrationConfigEntity,
                      prompt_messages: list,
                      text: str,
                      stream: bool) -> None:
        """
        Direct output
        :param queue_manager: application queue manager
        :param app_orchestration_config: app orchestration config
        :param prompt_messages: prompt messages
        :param text: text
        :param stream: stream
        :return:
        """
        if stream:
            index = 0
            for token in text:
                queue_manager.publish_chunk_message(LLMResultChunk(
                    model=app_orchestration_config.model_config.model,
                    prompt_messages=prompt_messages,
                    delta=LLMResultChunkDelta(
                        index=index,
                        message=AssistantPromptMessage(content=token)
                    )
                ))
                index += 1
                time.sleep(0.01)

        queue_manager.publish_message_end(
            llm_result=LLMResult(
                model=app_orchestration_config.model_config.model,
                prompt_messages=prompt_messages,
                message=AssistantPromptMessage(content=text),
                usage=LLMUsage.empty_usage()
            )
        )
