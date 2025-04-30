from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from core.entities.parameter_entities import (
    AppSelectorScope,
    CommonParameterType,
    ModelSelectorScope,
    ToolSelectorScope,
)
from core.model_runtime.entities.model_entities import ModelType
from core.tools.entities.common_entities import I18nObject


class ProviderQuotaType(Enum):
    """
    提供商配额类型枚举类
    
    定义不同类型的提供商配额：
    - PAID: 托管付费配额
    - FREE: 第三方免费配额
    - TRIAL: 托管试用配额
    """

    PAID = "paid"
    """hosted paid quota"""

    FREE = "free"
    """third-party free quota"""

    TRIAL = "trial"
    """hosted trial quota"""

    @staticmethod
    def value_of(value):
        """
        根据值获取对应的枚举成员
        
        :param value: 要查找的值
        :return: 对应的枚举成员
        :raises ValueError: 如果找不到对应的枚举成员
        """
        for member in ProviderQuotaType:
            if member.value == value:
                return member
        raise ValueError(f"No matching enum found for value '{value}'")


class QuotaUnit(Enum):
    """
    配额单位枚举类
    
    定义配额的不同计量单位：
    - TIMES: 按次数计算
    - TOKENS: 按token数量计算
    - CREDITS: 按积分计算
    """

    TIMES = "times"
    TOKENS = "tokens"
    CREDITS = "credits"


class SystemConfigurationStatus(Enum):
    """
    系统配置状态枚举类
    
    定义系统配置的不同状态：
    - ACTIVE: 配置处于活动状态
    - QUOTA_EXCEEDED: 配额已超出限制
    - UNSUPPORTED: 配置不受支持
    """

    ACTIVE = "active"
    QUOTA_EXCEEDED = "quota-exceeded"
    UNSUPPORTED = "unsupported"


class RestrictModel(BaseModel):
    """
    限制模型实体类
    
    用于定义受限制的模型配置，包含模型的基本信息。
    
    属性：
    - model: 模型名称
    - base_model_name: 基础模型名称（可选）
    - model_type: 模型类型
    """

    model: str
    base_model_name: Optional[str] = None
    model_type: ModelType

    # pydantic配置，保护命名空间
    model_config = ConfigDict(protected_namespaces=())


class QuotaConfiguration(BaseModel):
    """
    配额配置实体类
    
    定义提供商的配额配置信息，包括配额类型、单位、限制和使用情况。
    
    属性：
    - quota_type: 配额类型
    - quota_unit: 配额单位
    - quota_limit: 配额限制
    - quota_used: 已使用配额
    - is_valid: 配额是否有效
    - restrict_models: 受限制的模型列表
    """

    quota_type: ProviderQuotaType
    quota_unit: QuotaUnit
    quota_limit: int
    quota_used: int
    is_valid: bool
    restrict_models: list[RestrictModel] = []


class SystemConfiguration(BaseModel):
    """
    系统配置实体类
    
    定义提供商的系统级配置，包括启用状态、当前配额类型和凭证信息。
    
    属性：
    - enabled: 是否启用
    - current_quota_type: 当前配额类型
    - quota_configurations: 配额配置列表
    - credentials: 凭证信息
    """

    enabled: bool
    current_quota_type: Optional[ProviderQuotaType] = None
    quota_configurations: list[QuotaConfiguration] = []
    credentials: Optional[dict] = None


class CustomProviderConfiguration(BaseModel):
    """
    自定义提供商配置实体类
    
    用于存储提供商的自定义配置信息。
    
    属性：
    - credentials: 凭证信息字典
    """

    credentials: dict


class CustomModelConfiguration(BaseModel):
    """
    自定义模型配置实体类
    
    定义单个模型的自定义配置信息。
    
    属性：
    - model: 模型名称
    - model_type: 模型类型
    - credentials: 凭证信息
    """

    model: str
    model_type: ModelType
    credentials: dict

    # pydantic配置，保护命名空间
    model_config = ConfigDict(protected_namespaces=())


class CustomConfiguration(BaseModel):
    """
    自定义配置实体类
    
    包含提供商和模型的自定义配置信息。
    
    属性：
    - provider: 提供商自定义配置
    - models: 模型自定义配置列表
    """

    provider: Optional[CustomProviderConfiguration] = None
    models: list[CustomModelConfiguration] = []


class ModelLoadBalancingConfiguration(BaseModel):
    """
    模型负载均衡配置实体类
    
    定义模型的负载均衡配置信息。
    
    属性：
    - id: 配置ID
    - name: 配置名称
    - credentials: 凭证信息
    """

    id: str
    name: str
    credentials: dict


class ModelSettings(BaseModel):
    """
    模型设置实体类
    
    定义模型的基本设置，包括启用状态和负载均衡配置。
    
    属性：
    - model: 模型名称
    - model_type: 模型类型
    - enabled: 是否启用
    - load_balancing_configs: 负载均衡配置列表
    """

    model: str
    model_type: ModelType
    enabled: bool = True
    load_balancing_configs: list[ModelLoadBalancingConfiguration] = []

    # pydantic配置，保护命名空间
    model_config = ConfigDict(protected_namespaces=())


class BasicProviderConfig(BaseModel):
    """
    基础提供商配置实体类
    
    定义提供商配置的基本类型和名称。
    
    属性：
    - type: 配置类型
    - name: 配置名称
    """

    class Type(Enum):
        """
        配置类型枚举类
        
        定义不同类型的配置：
        - SECRET_INPUT: 密钥输入
        - TEXT_INPUT: 文本输入
        - SELECT: 选择器
        - BOOLEAN: 布尔值
        - APP_SELECTOR: 应用选择器
        - MODEL_SELECTOR: 模型选择器
        - TOOLS_SELECTOR: 工具选择器
        """

        SECRET_INPUT = CommonParameterType.SECRET_INPUT.value
        TEXT_INPUT = CommonParameterType.TEXT_INPUT.value
        SELECT = CommonParameterType.SELECT.value
        BOOLEAN = CommonParameterType.BOOLEAN.value
        APP_SELECTOR = CommonParameterType.APP_SELECTOR.value
        MODEL_SELECTOR = CommonParameterType.MODEL_SELECTOR.value
        TOOLS_SELECTOR = CommonParameterType.TOOLS_SELECTOR.value

        @classmethod
        def value_of(cls, value: str) -> "ProviderConfig.Type":
            """
            根据值获取对应的配置类型
            
            :param value: 配置类型值
            :return: 配置类型枚举
            :raises ValueError: 如果找不到对应的配置类型
            """
            for mode in cls:
                if mode.value == value:
                    return mode
            raise ValueError(f"invalid mode value {value}")

    type: Type = Field(..., description="配置类型")
    name: str = Field(..., description="配置名称")


class ProviderConfig(BasicProviderConfig):
    """
    提供商配置实体类
    
    扩展基础提供商配置，添加更多配置选项和详细信息。
    
    属性：
    - scope: 配置作用域
    - required: 是否必需
    - default: 默认值
    - options: 选项列表
    - label: 标签（支持国际化）
    - help: 帮助信息（支持国际化）
    - url: 相关URL
    - placeholder: 占位符文本（支持国际化）
    """

    class Option(BaseModel):
        """
        配置选项实体类
        
        定义配置选项的值和标签。
        
        属性：
        - value: 选项值
        - label: 选项标签（支持国际化）
        """

        value: str = Field(..., description="选项值")
        label: I18nObject = Field(..., description="选项标签")

    scope: AppSelectorScope | ModelSelectorScope | ToolSelectorScope | None = None
    required: bool = False
    default: Optional[Union[int, str]] = None
    options: Optional[list[Option]] = None
    label: Optional[I18nObject] = None
    help: Optional[I18nObject] = None
    url: Optional[str] = None
    placeholder: Optional[I18nObject] = None

    def to_basic_provider_config(self) -> BasicProviderConfig:
        """
        转换为基础提供商配置
        
        :return: 基础提供商配置实例
        """
        return BasicProviderConfig(type=self.type, name=self.name)
