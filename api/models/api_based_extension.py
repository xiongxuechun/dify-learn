import enum

from sqlalchemy import func

from .engine import db
from .types import StringUUID


class APIBasedExtensionPoint(enum.Enum):
    """
    API扩展点枚举
    
    定义系统中可以通过API扩展的功能点。
    每个枚举值代表一个可以被外部API扩展或集成的系统功能。
    """
    APP_EXTERNAL_DATA_TOOL_QUERY = "app.external_data_tool.query"  # 应用外部数据工具查询扩展点
    PING = "ping"                                                  # 连接测试扩展点
    APP_MODERATION_INPUT = "app.moderation.input"                  # 应用输入内容审核扩展点
    APP_MODERATION_OUTPUT = "app.moderation.output"                # 应用输出内容审核扩展点


class APIBasedExtension(db.Model):  # type: ignore[name-defined]
    """
    基于API的扩展模型
    
    表示通过外部API实现的系统功能扩展。
    租户可以通过配置外部API来扩展系统的特定功能点。
    """
    __tablename__ = "api_based_extensions"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="api_based_extension_pkey"),
        db.Index("api_based_extension_tenant_idx", "tenant_id"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))     # 扩展ID
    tenant_id = db.Column(StringUUID, nullable=False)                            # 所属租户ID
    name = db.Column(db.String(255), nullable=False)                             # 扩展名称
    api_endpoint = db.Column(db.String(255), nullable=False)                     # API端点URL
    api_key = db.Column(db.Text, nullable=False)                                 # 访问API所需的密钥
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 创建时间
