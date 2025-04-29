import json

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB

from models.base import Base

from .engine import db
from .types import StringUUID


class DataSourceOauthBinding(db.Model):  # type: ignore[name-defined]
    """
    数据源OAuth绑定模型
    
    存储通过OAuth授权连接的外部数据源信息。
    用于管理与第三方系统(如Google Drive, Notion等)的OAuth授权连接。
    """
    __tablename__ = "data_source_oauth_bindings"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="source_binding_pkey"),
        db.Index("source_binding_tenant_id_idx", "tenant_id"),
        db.Index("source_info_idx", "source_info", postgresql_using="gin"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))  # 绑定ID
    tenant_id = db.Column(StringUUID, nullable=False)                         # 所属租户ID
    access_token = db.Column(db.String(255), nullable=False)                  # OAuth访问令牌
    provider = db.Column(db.String(255), nullable=False)                      # 数据源提供商(如google, notion等)
    source_info = db.Column(JSONB, nullable=False)                            # 数据源详细信息(JSON格式)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 更新时间
    disabled = db.Column(db.Boolean, nullable=True, server_default=db.text("false"))  # 是否禁用


class DataSourceApiKeyAuthBinding(Base):
    """
    数据源API密钥认证绑定模型
    
    存储通过API密钥连接的外部数据源信息。
    用于管理需要API密钥认证的第三方数据服务(如OpenAI, Jira API等)。
    """
    __tablename__ = "data_source_api_key_auth_bindings"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="data_source_api_key_auth_binding_pkey"),
        db.Index("data_source_api_key_auth_binding_tenant_id_idx", "tenant_id"),
        db.Index("data_source_api_key_auth_binding_provider_idx", "provider"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))  # 绑定ID
    tenant_id = db.Column(StringUUID, nullable=False)                         # 所属租户ID
    category = db.Column(db.String(255), nullable=False)                      # 数据源类别(如ai_service, database等)
    provider = db.Column(db.String(255), nullable=False)                      # 数据源提供商
    credentials = db.Column(db.Text, nullable=True)                           # 认证凭据(JSON格式，通常包含API密钥)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 更新时间
    disabled = db.Column(db.Boolean, nullable=True, server_default=db.text("false"))  # 是否禁用

    def to_dict(self):
        """
        将模型对象转换为字典
        
        用于API响应和序列化处理。
        
        :return: 包含对象所有字段的字典
        """
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "category": self.category,
            "provider": self.provider,
            "credentials": json.loads(self.credentials),
            "created_at": self.created_at.timestamp(),
            "updated_at": self.updated_at.timestamp(),
            "disabled": self.disabled,
        }
