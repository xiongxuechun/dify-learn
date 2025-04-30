from collections.abc import Sequence
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict

from core.model_runtime.entities.common_entities import I18nObject
from core.model_runtime.entities.model_entities import ModelType, ProviderModel
from core.model_runtime.entities.provider_entities import ProviderEntity


class ModelStatus(Enum):
    """
    模型状态枚举类
    
    定义模型可能的各种状态，用于标识模型的可用性和状态。
    
    状态包括：
    - ACTIVE: 模型处于活动状态，可以正常使用
    - NO_CONFIGURE: 模型未配置，需要完成配置才能使用
    - QUOTA_EXCEEDED: 模型配额已超出限制
    - NO_PERMISSION: 没有使用该模型的权限
    - DISABLED: 模型已被禁用
    """

    ACTIVE = "active"
    NO_CONFIGURE = "no-configure"
    QUOTA_EXCEEDED = "quota-exceeded"
    NO_PERMISSION = "no-permission"
    DISABLED = "disabled"


class SimpleModelProviderEntity(BaseModel):
    """
    简化提供商实体类
    
    提供商的简化表示，包含基本信息如名称、标签、图标等。
    用于在不需要完整提供商信息时的轻量级表示。
    
    属性：
    - provider: 提供商名称
    - label: 提供商标签（支持国际化）
    - icon_small: 小图标（支持国际化）
    - icon_large: 大图标（支持国际化）
    - supported_model_types: 支持的模型类型列表
    """

    provider: str
    label: I18nObject
    icon_small: Optional[I18nObject] = None
    icon_large: Optional[I18nObject] = None
    supported_model_types: list[ModelType]

    def __init__(self, provider_entity: ProviderEntity) -> None:
        """
        初始化简化提供商实体
        
        从完整的提供商实体中提取必要信息创建简化版本。
        
        :param provider_entity: 完整的提供商实体
        """
        super().__init__(
            provider=provider_entity.provider,
            label=provider_entity.label,
            icon_small=provider_entity.icon_small,
            icon_large=provider_entity.icon_large,
            supported_model_types=provider_entity.supported_model_types,
        )


class ProviderModelWithStatusEntity(ProviderModel):
    """
    带状态的提供商模型实体类
    
    扩展基础提供商模型，添加状态信息和负载均衡配置。
    用于表示模型的实际可用状态和配置。
    
    属性：
    - status: 模型当前状态
    - load_balancing_enabled: 是否启用负载均衡
    """

    status: ModelStatus
    load_balancing_enabled: bool = False


class ModelWithProviderEntity(ProviderModelWithStatusEntity):
    """
    带提供商的模型实体类
    
    扩展带状态的提供商模型，添加提供商信息。
    用于表示完整的模型信息，包括其所属提供商。
    
    属性：
    - provider: 模型所属的提供商信息
    """

    provider: SimpleModelProviderEntity


class DefaultModelProviderEntity(BaseModel):
    """
    默认模型提供商实体类
    
    表示默认的模型提供商配置，包含提供商的基本信息。
    用于系统默认配置和回退选项。
    
    属性：
    - provider: 提供商名称
    - label: 提供商标签（支持国际化）
    - icon_small: 小图标（支持国际化）
    - icon_large: 大图标（支持国际化）
    - supported_model_types: 支持的模型类型列表
    """

    provider: str
    label: I18nObject
    icon_small: Optional[I18nObject] = None
    icon_large: Optional[I18nObject] = None
    supported_model_types: Sequence[ModelType] = []


class DefaultModelEntity(BaseModel):
    """
    默认模型实体类
    
    表示系统的默认模型配置，包含模型和其提供商的信息。
    用于系统默认配置和回退选项。
    
    属性：
    - model: 模型名称
    - model_type: 模型类型
    - provider: 模型所属的提供商信息
    """

    model: str
    model_type: ModelType
    provider: DefaultModelProviderEntity

    # pydantic配置，保护命名空间
    model_config = ConfigDict(protected_namespaces=())
