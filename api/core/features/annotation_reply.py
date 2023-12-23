import logging

from flask import current_app

from core.application_queue_manager import ApplicationQueueManager
from core.embedding.cached_embedding import CacheEmbedding
from core.entities.application_entities import ModelConfigEntity, InvokeFrom
from core.index.vector_index.vector_index import VectorIndex
from extensions.ext_database import db
from models.dataset import Dataset
from models.model import App, Message, AppAnnotationSetting
from services.annotation_service import AppAnnotationService
from services.dataset_service import DatasetCollectionBindingService

logger = logging.getLogger(__name__)


class AnnotationReplyFeature:
    def query(self, queue_manager: ApplicationQueueManager,
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
        annotation_setting = db.session.query(AppAnnotationSetting).filter(
            AppAnnotationSetting.app_id == app_record.id).first()

        if not annotation_setting:
            return False

        collection_binding_detail = annotation_setting.collection_binding_detail

        try:
            score_threshold = annotation_setting.score_threshold or 1
            embedding_provider_name = collection_binding_detail.provider_name
            embedding_model_name = collection_binding_detail.model_name

            # get embedding model
            embeddings = CacheEmbedding(model_config)

            dataset_collection_binding = DatasetCollectionBindingService.get_dataset_collection_binding(
                embedding_provider_name,
                embedding_model_name,
                'annotation'
            )

            dataset = Dataset(
                id=app_record.id,
                tenant_id=app_record.tenant_id,
                indexing_technique='high_quality',
                embedding_model_provider=embedding_provider_name,
                embedding_model=embedding_model_name,
                collection_binding_id=dataset_collection_binding.id
            )

            vector_index = VectorIndex(
                dataset=dataset,
                config=current_app.config,
                embeddings=embeddings,
                attributes=['doc_id', 'annotation_id', 'app_id']
            )

            documents = vector_index.search(
                query=query,
                search_type='similarity_score_threshold',
                search_kwargs={
                    'k': 1,
                    'score_threshold': score_threshold,
                    'filter': {
                        'group_id': [dataset.id]
                    }
                }
            )

            if documents:
                annotation_id = documents[0].metadata['annotation_id']
                score = documents[0].metadata['score']
                annotation = AppAnnotationService.get_annotation_by_id(annotation_id)
                if annotation:
                    if invoke_from in [InvokeFrom.SERVICE_API, InvokeFrom.WEB_APP]:
                        from_source = 'api'
                    else:
                        from_source = 'console'

                    # insert annotation history
                    AppAnnotationService.add_annotation_history(annotation.id,
                                                                app_record.id,
                                                                annotation.question,
                                                                annotation.content,
                                                                query,
                                                                user_id,
                                                                message.id,
                                                                from_source,
                                                                score)

                    queue_manager.publish_annotation_reply(
                        message_annotation_id=annotation.id
                    )
                    return True
        except Exception as e:
            logger.warning(f'Query annotation failed, exception: {str(e)}.')
            return False

        return False
