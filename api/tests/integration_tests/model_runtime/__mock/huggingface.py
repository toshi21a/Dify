import os
from typing import Any, Dict, List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from huggingface_hub import InferenceClient

from core.utils.type_helper import get_bool, get_bool_from_sys_env
from tests.integration_tests.model_runtime.__mock.huggingface_chat import MockHuggingfaceChatClass

MOCK = get_bool_from_sys_env('MOCK_SWITCH')

@pytest.fixture
def setup_huggingface_mock(request, monkeypatch: MonkeyPatch):
    if MOCK:
        monkeypatch.setattr(InferenceClient, "text_generation", MockHuggingfaceChatClass.text_generation)
    
    yield

    if MOCK:
        monkeypatch.undo()