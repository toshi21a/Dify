from typing import Any, Dict, List
from core.tools.entities.tool_entities import ToolInvokeMessage, ToolProviderType, ToolParamter, ToolParamterOption
from core.tools.provider.tool import Tool
from core.tools.entities.common_entities import I18nObject
from core.tools.provider.tool_provider import ToolProviderController
from core.model_runtime.entities.message_entities import PromptMessage

from extensions.ext_database import db
from models.tools import PublishedAppTool
from models.model import App, AppModelConfig

import logging

logger = logging.getLogger(__name__)

class AppBasedToolProviderEntity(ToolProviderController):
    @property
    def app_type(self) -> ToolProviderType:
        return ToolProviderType.APP_BASED
    
    def invoke(self, 
               tool_id: int, tool_name: str, 
               tool_paramters: Dict[str, Any], 
               credentials: Dict[str, Any], 
               prompt_messages: List[PromptMessage]
        ) -> List[ToolInvokeMessage]:
        """
            invoke app based assistant

            tool_name: the name of the tool, defined in `get_tools`
            tool_paramters: the parameters of the tool
            credentials: the credentials of the tool
            prompt_messages: the prompt messages that the tool can use

            :return: the messages that the tool wants to send to the user
        """

    def _validate_credentials(self, tool_name: str, credentials: Dict[str, Any]) -> None:
        pass

    def validate_parameters(self, tool_name: str, tool_parameters: Dict[str, Any]) -> None:
        pass

    def get_tools(self, user_id: str) -> List[Tool]:
        db_tools: List[PublishedAppTool] = db.session.query(PublishedAppTool).filter(
            PublishedAppTool.user_id == user_id,
        ).all()

        if not db_tools or len(db_tools) == 0:
            return []

        tools: List[Tool] = []

        for db_tool in db_tools:
            tool = {
                'identity': {
                    'author': db_tool.author,
                    'name': db_tool.tool_name,
                    'label': {
                        'en_US': db_tool.tool_name,
                        'zh_Hans': db_tool.tool_name
                    },
                    'icon': ''
                },
                'description': {
                    'human': {
                        'en_US': db_tool.description_i18n.en_US,
                        'zh_Hans': db_tool.description_i18n.zh_Hans
                    },
                    'llm': db_tool.llm_description
                },
                'parameters': []
            }
            # get app from db
            app: App = db_tool.app

            if not app:
                logger.error(f"app {db_tool.app_id} not found")
                continue

            app_model_config: AppModelConfig = app.app_model_config
            user_input_form_list = app_model_config.user_input_form_list
            for input_form in user_input_form_list:
                # get type
                form_type = input_form.keys()[0]
                default = input_form[form_type]['default']
                required = input_form[form_type]['required']
                label = input_form[form_type]['label']
                variable_name = input_form[form_type]['variable_name']
                options = input_form[form_type].get('options', [])
                if form_type == 'paragraph' or form_type == 'text-input':
                    tool['parameters'].append(ToolParamter(
                        name=variable_name,
                        label=I18nObject(
                            en_US=label,
                            zh_Hans=label
                        ),
                        human_description=I18nObject(
                            en_US=label,
                            zh_Hans=label
                        ),
                        llm_description=label,
                        form=ToolParamter.ToolParameterForm.FORM,
                        type=ToolParamter.ToolParameterType.STRING,
                        required=required,
                        default=default
                    ))
                elif form_type == 'select':
                    tool['parameters'].append(ToolParamter(
                        name=variable_name,
                        label=I18nObject(
                            en_US=label,
                            zh_Hans=label
                        ),
                        human_description=I18nObject(
                            en_US=label,
                            zh_Hans=label
                        ),
                        llm_description=label,
                        form=ToolParamter.ToolParameterForm.FORM,
                        type=ToolParamter.ToolParameterType.SELECT,
                        required=required,
                        default=default,
                        options=[ToolParamterOption(
                            value=option,
                            label=I18nObject(
                                en_US=option,
                                zh_Hans=option
                            )
                        ) for option in options]
                    ))

            tools.append(Tool(**tool))
        return tools