import json
import uuid

import pandas as pd
from flask_login import current_user
from sqlalchemy import or_
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import NotFound

from extensions.ext_database import db
from extensions.ext_redis import redis_client
from models.model import MessageAnnotation, Message, App, AppAnnotationHitHistory
from tasks.annotation.add_annotation_to_index_task import add_annotation_to_index_task
from tasks.annotation.enable_annotation_reply_task import enable_annotation_reply_task
from tasks.annotation.disable_annotation_reply_task import disable_annotation_reply_task
from tasks.annotation.update_annotation_to_index_task import update_annotation_to_index_task
from tasks.annotation.delete_annotation_index_task import delete_annotation_index_task
from tasks.annotation.batch_import_annotations_task import batch_import_annotations_task


class AppAnnotationService:
    @classmethod
    def up_insert_app_annotation_from_message(cls, args: dict, app_id: str) -> MessageAnnotation:
        # get app info
        app = db.session.query(App).filter(
            App.id == app_id,
            App.tenant_id == current_user.current_tenant_id,
            App.status == 'normal'
        ).first()

        if not app:
            raise NotFound("App not found")

        message_id = str(args['message_id'])
        # get message info
        message = db.session.query(Message).filter(
            Message.id == message_id,
            Message.app_id == app.id
        ).first()

        if not message:
            raise NotFound("Message Not Exists.")

        annotation = message.annotation
        # save the message annotation
        if annotation:
            annotation.content = args['content']
            annotation.question = args['question']
        else:
            annotation = MessageAnnotation(
                app_id=app.id,
                conversation_id=message.conversation_id,
                message_id=message.id,
                content=args['content'],
                question=args['question'],
                account_id=current_user.id
            )
            db.session.add(annotation)
        db.session.commit()
        # if annotation reply is enabled , add annotation to index
        app_model_config = app.app_model_config
        if app_model_config:
            if app_model_config.annotation_reply:
                annotation_reply_config = json.loads(app_model_config.annotation_reply)
                if annotation_reply_config['enabled']:
                    add_annotation_to_index_task.delay(annotation.id, args['question'], current_user.current_tenant_id,
                                                       app_id, annotation_reply_config['embedding_model'][
                                                           'embedding_provider_name'],
                                                       annotation_reply_config['embedding_model'][
                                                           'embedding_model_name'])
        return annotation

    @classmethod
    def enable_app_annotation(cls, args: dict, app_id: str) -> dict:
        enable_app_annotation_key = 'enable_app_annotation_{}'.format(str(app_id))
        cache_result = redis_client.get(enable_app_annotation_key)
        if cache_result is not None:
            return {
                'job_id': cache_result,
                'job_status': 'processing'
            }

        # async job
        job_id = str(uuid.uuid4())
        enable_app_annotation_job_key = 'enable_app_annotation_job_{}'.format(str(job_id))
        # send batch add segments task
        redis_client.setnx(enable_app_annotation_job_key, 'waiting')
        enable_annotation_reply_task.delay(str(job_id), app_id, current_user.current_tenant_id,
                                           args['embedding_provider_name'], args['embedding_model_name'])
        return {
            'job_id': job_id,
            'job_status': 'waiting'
        }

    @classmethod
    def disable_app_annotation(cls, args: dict, app_id: str) -> dict:
        disable_app_annotation_key = 'disable_app_annotation_{}'.format(str(app_id))
        cache_result = redis_client.get(disable_app_annotation_key)
        if cache_result is not None:
            return {
                'job_id': cache_result,
                'job_status': 'processing'
            }

        # async job
        job_id = str(uuid.uuid4())
        disable_app_annotation_job_key = 'disable_app_annotation_job_{}'.format(str(job_id))
        # send batch add segments task
        redis_client.setnx(disable_app_annotation_job_key, 'waiting')
        disable_annotation_reply_task.delay(str(job_id), app_id, current_user.current_tenant_id,
                                            args['embedding_provider_name'], args['embedding_model_name'])
        return {
            'job_id': job_id,
            'job_status': 'waiting'
        }

    @classmethod
    def get_annotation_list_by_app_id(cls, app_id: str, page: int, limit: int, keyword: str):
        # get app info
        app = db.session.query(App).filter(
            App.id == app_id,
            App.tenant_id == current_user.current_tenant_id,
            App.status == 'normal'
        ).first()

        if not app:
            raise NotFound("App not found")
        if keyword:
            annotations = (db.session.query(MessageAnnotation)
                           .filter(MessageAnnotation.app_id == app_id)
                           .filter(
                or_(
                    Message.query.ilike('%{}%'.format(keyword)),
                    Message.answer.ilike('%{}%'.format(keyword))
                )
            )
                           .order_by(MessageAnnotation.created_at.desc())
                           .paginate(page=page, per_page=limit, max_per_page=100, error_out=False))
        else:
            annotations = (db.session.query(MessageAnnotation)
                           .filter(MessageAnnotation.app_id == app_id)
                           .order_by(MessageAnnotation.created_at.desc())
                           .paginate(page=page, per_page=limit, max_per_page=100, error_out=False))
        return annotations.items, annotations.total

    @classmethod
    def export_annotation_list_by_app_id(cls, app_id: str):
        # get app info
        app = db.session.query(App).filter(
            App.id == app_id,
            App.tenant_id == current_user.current_tenant_id,
            App.status == 'normal'
        ).first()

        if not app:
            raise NotFound("App not found")
        annotations = (db.session.query(MessageAnnotation)
                       .filter(MessageAnnotation.app_id == app_id)
                       .order_by(MessageAnnotation.created_at.desc()).all())
        return annotations

    @classmethod
    def insert_app_annotation_directly(cls, args: dict, app_id: str) -> MessageAnnotation:
        # get app info
        app = db.session.query(App).filter(
            App.id == app_id,
            App.tenant_id == current_user.current_tenant_id,
            App.status == 'normal'
        ).first()

        if not app:
            raise NotFound("App not found")

        annotation = MessageAnnotation(
            app_id=app.id,
            content=args['content'],
            question=args['question'],
            account_id=current_user.id
        )
        db.session.add(annotation)
        db.session.commit()
        # if annotation reply is enabled , add annotation to index
        app_model_config = app.app_model_config
        if app_model_config:
            if app_model_config.annotation_reply:
                annotation_reply_config = json.loads(app_model_config.annotation_reply)
                if annotation_reply_config['enabled']:
                    add_annotation_to_index_task.delay(annotation.id, annotation.question,
                                                       current_user.current_tenant_id,
                                                       app_id, annotation_reply_config['embedding_model'][
                                                           'embedding_provider_name'],
                                                       annotation_reply_config['embedding_model'][
                                                           'embedding_model_name'])
        return annotation

    @classmethod
    def update_app_annotation_directly(cls, args: dict, app_id: str, annotation_id: str):
        # get app info
        app = db.session.query(App).filter(
            App.id == app_id,
            App.tenant_id == current_user.current_tenant_id,
            App.status == 'normal'
        ).first()

        if not app:
            raise NotFound("App not found")

        annotation = db.session.query(MessageAnnotation).filter(MessageAnnotation.id == annotation_id).first()

        if not annotation:
            raise NotFound("Annotation not found")

        annotation.content = args['content']
        annotation.question = args['question']

        db.session.commit()
        # if annotation reply is enabled , add annotation to index
        app_model_config = app.app_model_config
        if app_model_config:
            if app_model_config.annotation_reply:
                annotation_reply_config = json.loads(app_model_config.annotation_reply)
                if annotation_reply_config['enabled']:
                    update_annotation_to_index_task.delay(annotation.id, annotation.question,
                                                          current_user.current_tenant_id,
                                                          app_id, annotation_reply_config['embedding_model'][
                                                              'embedding_provider_name'],
                                                          annotation_reply_config['embedding_model'][
                                                              'embedding_model_name'])
        return annotation

    @classmethod
    def delete_app_annotation(cls, app_id: str, annotation_id: str):
        # get app info
        app = db.session.query(App).filter(
            App.id == app_id,
            App.tenant_id == current_user.current_tenant_id,
            App.status == 'normal'
        ).first()

        if not app:
            raise NotFound("App not found")

        annotation = db.session.query(MessageAnnotation).filter(MessageAnnotation.id == annotation_id).first()

        if not annotation:
            raise NotFound("Annotation not found")

        db.session.delete(annotation)

        # if annotation reply is enabled , delete annotation index
        app_model_config = app.app_model_config
        if app_model_config:
            if app_model_config.annotation_reply:
                annotation_reply_config = json.loads(app_model_config.annotation_reply)
                if annotation_reply_config['enabled']:
                    delete_annotation_index_task.delay(annotation.id, app_id,
                                                       current_user.current_tenant_id,
                                                       app_id, annotation_reply_config['embedding_model'][
                                                           'embedding_provider_name'],
                                                       annotation_reply_config['embedding_model'][
                                                           'embedding_model_name'])

    @classmethod
    def batch_import_app_annotations(cls, app_id, file: FileStorage) -> dict:
        # get app info
        app = db.session.query(App).filter(
            App.id == app_id,
            App.tenant_id == current_user.current_tenant_id,
            App.status == 'normal'
        ).first()

        if not app:
            raise NotFound("App not found")

        try:
            # Skip the first row
            df = pd.read_csv(file)
            result = []
            for index, row in df.iterrows():
                content = {
                    'question': row[0],
                    'content': row[1]
                }
                result.append(content)
            if len(result) == 0:
                raise ValueError("The CSV file is empty.")
            # async job
            job_id = str(uuid.uuid4())
            indexing_cache_key = 'app_annotation_batch_import_{}'.format(str(job_id))
            # send batch add segments task
            redis_client.setnx(indexing_cache_key, 'waiting')
            batch_import_annotations_task.delay(str(job_id), result, app_id,
                                                current_user.current_tenant_id, current_user.id)
        except Exception as e:
            return {
                'error_msg': str(e)
            }
        return {
            'job_id': job_id,
            'job_status': 'waiting'
        }

    @classmethod
    def get_annotation_hit_histories(cls, app_id: str, annotation_id: str) -> list[AppAnnotationHitHistory]:
        # get app info
        app = db.session.query(App).filter(
            App.id == app_id,
            App.tenant_id == current_user.current_tenant_id,
            App.status == 'normal'
        ).first()

        if not app:
            raise NotFound("App not found")

        annotation = db.session.query(MessageAnnotation).filter(MessageAnnotation.id == annotation_id).first()

        if not annotation:
            raise NotFound("Annotation not found")

        annotation_hit_histories = (db.session.query(AppAnnotationHitHistory)
                                    .filter(AppAnnotationHitHistory.app_id == app_id,
                                            AppAnnotationHitHistory.annotation_id == annotation_id,
                                            )
                                    .all())
        return annotation_hit_histories

    @classmethod
    def get_annotation_by_id(cls, annotation_id: str) -> MessageAnnotation | None:
        annotation = db.session.query(MessageAnnotation).filter(MessageAnnotation.id == annotation_id).first()

        if not annotation:
            return None
        return annotation

    @classmethod
    def add_annotation_history(cls, annotation_id: str, app_id: str, query: str, user_id: str, from_source: str):
        annotation = AppAnnotationHitHistory(
            annotation_id=annotation_id,
            app_id=app_id,
            account_id=user_id,
            question=query,
            source=from_source.id
        )
        db.session.add(annotation)
        db.session.commit()
