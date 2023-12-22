import os
import pytest

from core.model_runtime.entities.rerank_entities import RerankResult
from core.model_runtime.errors.validate import CredentialsValidateFailedError
from core.model_runtime.model_providers.xinference.rerank.rerank import XinferenceRerankModel


def test_validate_credentials():
    model = XinferenceRerankModel()

    with pytest.raises(CredentialsValidateFailedError):
        model.validate_credentials(
            model='bge-reranker-base',
            credentials={
                'server_url': 'awdawdaw',
                'model_type': 'embeddings',
                'model_name': 'NOT IMPORTANT',
                'model_uid': os.environ.get('XINFERENCE_RERANK_MODEL_UID')
            }
        )

    model.validate_credentials(
        model='bge-reranker-base',
        credentials={
            'server_url': os.environ.get('XINFERENCE_SERVER_URL'),
            'model_type': 'embeddings',
            'model_name': 'NOT IMPORTANT',
            'model_uid': os.environ.get('XINFERENCE_RERANK_MODEL_UID')
        }
    )


def test_invoke_model():
    model = XinferenceRerankModel()

    result = model.invoke(
        model='bge-reranker-base',
        credentials={
            'server_url': os.environ.get('XINFERENCE_SERVER_URL'),
            'model_type': 'embeddings',
            'model_name': 'NOT IMPORTANT',
            'model_uid': os.environ.get('XINFERENCE_RERANK_MODEL_UID')
        },
        query="Who is Kasumi?",
        docs=[
            "Kasumi is a girl's name of Japanese origin meaning \"mist\".",
            "Her music is a kawaii bass, a mix of future bass, pop, and kawaii music ",
            "and she leads a team named PopiParty."
        ],
        score_threshold=0.8
    )

    assert isinstance(result, RerankResult)
    assert len(result.docs) == 1
    assert result.docs[0].index == 0
    assert result.docs[0].score >= 0.8
