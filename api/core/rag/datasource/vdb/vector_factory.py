import json
from typing import Any, cast

from flask import current_app

from core.embedding.cached_embedding import CacheEmbedding
from core.model_manager import ModelManager
from core.model_runtime.entities.model_entities import ModelType
from core.rag.datasource.entity.embedding import Embeddings
from core.rag.datasource.vdb.vector_base import BaseVector
from core.rag.models.document import Document
from extensions.ext_database import db
from models.dataset import Dataset, DatasetCollectionBinding


class Vector:
    def __init__(self, dataset: Dataset, attributes: list = None):
        if attributes is None:
            attributes = ['doc_id', 'dataset_id', 'document_id', 'doc_hash']
        self._dataset = dataset
        self._embeddings = self._get_embeddings()
        self._attributes = attributes
        self._vector_processor = self._init_vector()

    def _init_vector(self) -> BaseVector:
        config = current_app.config
        vector_type = config.get('VECTOR_STORE')

        if self._dataset.index_struct_dict:
            vector_type = self._dataset.index_struct_dict['type']

        if not vector_type:
            raise ValueError("Vector store must be specified.")

        if vector_type == "weaviate":
            from core.rag.datasource.vdb.weaviate.weaviate_vector import WeaviateConfig, WeaviateVector
            if self._dataset.index_struct_dict:
                class_prefix: str = self._dataset.index_struct_dict['vector_store']['class_prefix']
                collection_name = class_prefix
            else:
                dataset_id = self._dataset.id
                collection_name = "Vector_index_" + dataset_id.replace("-", "_") + '_Node'
                index_struct_dict = {
                    "type": 'weaviate',
                    "vector_store": {"class_prefix": collection_name}
                }
                self._dataset.index_struct = json.dumps(index_struct_dict)
            return WeaviateVector(
                collection_name=collection_name,
                config=WeaviateConfig(
                    endpoint=config.get('WEAVIATE_ENDPOINT'),
                    api_key=config.get('WEAVIATE_API_KEY'),
                    batch_size=int(config.get('WEAVIATE_BATCH_SIZE'))
                ),
                attributes=self._attributes
            )
        elif vector_type == "qdrant":
            from core.rag.datasource.vdb.qdrant.qdrant_vector import QdrantConfig, QdrantVector
            if self._dataset.collection_binding_id:
                dataset_collection_binding = db.session.query(DatasetCollectionBinding). \
                    filter(DatasetCollectionBinding.id == self._dataset.collection_binding_id). \
                    one_or_none()
                if dataset_collection_binding:
                    collection_name = dataset_collection_binding.collection_name
                else:
                    raise ValueError('Dataset Collection Bindings is not exist!')
            else:
                if self._dataset.index_struct_dict:
                    class_prefix: str = self.dataset.index_struct_dict['vector_store']['class_prefix']
                    collection_name = class_prefix
                else:
                    dataset_id = self._dataset.id
                    collection_name = "Vector_index_" + dataset_id.replace("-", "_") + '_Node'

            if not self._dataset.index_struct_dict:
                index_struct_dict = {
                    "type": 'qdrant',
                    "vector_store": {"class_prefix": collection_name}
                }
                self._dataset.index_struct = json.dumps(index_struct_dict)

            return QdrantVector(
                collection_name=collection_name,
                group_id=self._dataset.id,
                config=QdrantConfig(
                    endpoint=config.get('QDRANT_URL'),
                    api_key=config.get('QDRANT_API_KEY'),
                    root_path=current_app.root_path,
                    timeout=config.get('QDRANT_CLIENT_TIMEOUT')
                )
            )
        elif vector_type == "milvus":
            from core.rag.datasource.vdb.milvus.milvus_vector import MilvusConfig, MilvusVector
            if self._dataset.index_struct_dict:
                class_prefix: str = self._dataset.index_struct_dict['vector_store']['class_prefix']
                collection_name = class_prefix
            else:
                dataset_id = self._dataset.id
                collection_name = "Vector_index_" + dataset_id.replace("-", "_") + '_Node'
                index_struct_dict = {
                    "type": 'milvus',
                    "vector_store": {"class_prefix": collection_name}
                }
                self._dataset.index_struct = json.dumps(index_struct_dict)
            return MilvusVector(
                collection_name=collection_name,
                config=MilvusConfig(
                    host=config.get('MILVUS_HOST'),
                    port=config.get('MILVUS_PORT'),
                    user=config.get('MILVUS_USER'),
                    password=config.get('MILVUS_PASSWORD'),
                    secure=config.get('MILVUS_SECURE'),
                )
            )
        else:
            raise ValueError(f"Vector store {config.get('VECTOR_STORE')} is not supported.")

    def create(self, texts: list = None, **kwargs):
        if texts:
            embeddings = self._embeddings.embed_documents([document.page_content for document in texts])
            self._vector_processor.create(
                texts=texts,
                embeddings=embeddings,
                **kwargs
            )

    def add_texts(self, documents: list[Document], **kwargs):
        if kwargs.get('duplicate_check', False):
            documents = self._filter_duplicate_texts(documents)
        embeddings = self._embeddings.embed_documents([document.page_content for document in documents])
        self._vector_processor.add_texts(
            documents=documents,
            embeddings=embeddings,
            **kwargs
        )

    def text_exists(self, id: str) -> bool:
        return self._vector_processor.text_exists(id)

    def delete_by_ids(self, ids: list[str]) -> None:
        self._vector_processor.delete_by_ids(ids)

    def delete_by_metadata_field(self, key: str, value: str) -> None:
        self._vector_processor.delete_by_metadata_field(key, value)

    def search_by_vector(
            self, query: str,
            **kwargs: Any
    ) -> list[Document]:
        query_vector = self._embeddings.embed_query(query)
        return self._vector_processor.search_by_vector(query_vector, **kwargs)

    def search_by_full_text(
            self, query: str,
            **kwargs: Any
    ) -> list[Document]:
        return self._vector_processor.search_by_full_text(query, **kwargs)

    def delete(self) -> None:
        self._vector_processor.delete()

    def _get_embeddings(self) -> Embeddings:
        model_manager = ModelManager()

        embedding_model = model_manager.get_model_instance(
            tenant_id=self._dataset.tenant_id,
            provider=self._dataset.embedding_model_provider,
            model_type=ModelType.TEXT_EMBEDDING,
            model=self._dataset.embedding_model

        )
        return CacheEmbedding(embedding_model)

    def _filter_duplicate_texts(self, texts: list[Document]) -> list[Document]:
        for text in texts:
            doc_id = text.metadata['doc_id']
            exists_duplicate_node = self.text_exists(doc_id)
            if exists_duplicate_node:
                texts.remove(text)

        return texts

    def __getattr__(self, name):
        if self._vector_processor is not None:
            method = getattr(self._vector_processor, name)
            if callable(method):
                return method

        raise AttributeError(f"'vector_processor' object has no attribute '{name}'")
