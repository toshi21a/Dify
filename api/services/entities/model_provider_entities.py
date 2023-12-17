from enum import Enum
from typing import Optional

from pydantic import BaseModel

from core.entities.model_entities import ModelStatus
from core.entities.provider_entities import QuotaConfiguration
from core.model_runtime.entities.common_entities import I18nObject
from core.model_runtime.entities.model_entities import ModelType, ProviderModel
from core.model_runtime.entities.provider_entities import ConfigurateMethod, ProviderCredentialSchema, \
    ModelCredentialSchema, ProviderHelpEntity, SimpleProviderEntity
from models.provider import ProviderType, ProviderQuotaType


class CustomConfigurationStatus(Enum):
    """
    Enum class for custom configuration status.
    """
    ACTIVE = 'active'
    NO_CONFIGURE = 'no-configure'


class CustomConfigurationResponse(BaseModel):
    """
    Model class for provider custom configuration response.
    """
    status: CustomConfigurationStatus


class SystemConfigurationResponse(BaseModel):
    """
    Model class for provider system configuration response.
    """
    enabled: bool
    current_quota_type: Optional[ProviderQuotaType] = None
    quota_configurations: list[QuotaConfiguration] = []


class ProviderResponse(BaseModel):
    """
    Model class for provider response.
    """
    provider: str
    label: I18nObject
    description: Optional[I18nObject] = None
    icon_small: I18nObject
    icon_large: I18nObject
    background: Optional[I18nObject] = None
    help: Optional[ProviderHelpEntity] = None
    supported_model_types: list[ModelType]
    configurate_methods: list[ConfigurateMethod]
    provider_credential_schema: Optional[ProviderCredentialSchema] = None
    model_credential_schema: Optional[ModelCredentialSchema] = None
    preferred_provider_type: ProviderType
    custom_configuration: CustomConfigurationResponse
    system_configuration: SystemConfigurationResponse


class ModelResponse(ProviderModel):
    """
    Model class for model response.
    """
    status: ModelStatus


class ProviderWithModelsResponse(BaseModel):
    """
    Model class for provider with models response.
    """
    provider: str
    label: I18nObject
    icon_small: I18nObject
    icon_large: I18nObject
    status: CustomConfigurationStatus
    models: list[ModelResponse]


class DefaultModelResponse(BaseModel):
    """
    Default model entity.
    """
    model: str
    model_type: ModelType
    provider: SimpleProviderEntity
