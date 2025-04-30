import enum
import json

from flask_login import UserMixin  # type: ignore
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base

from .engine import db
from .types import StringUUID


class AccountStatus(enum.StrEnum):
    """
    账户状态枚举
    
    定义系统中账户可能的各种状态
    """
    PENDING = "pending"          # 待处理，账户已创建但未完成注册流程
    UNINITIALIZED = "uninitialized"  # 未初始化，账户创建但未设置必要信息
    ACTIVE = "active"            # 活跃，账户正常可用
    BANNED = "banned"            # 封禁，账户被管理员禁用
    CLOSED = "closed"            # 关闭，账户已被用户自行关闭


class Account(UserMixin, Base):
    """
    账户模型
    
    表示系统中的用户账户，继承Flask-Login的UserMixin以支持用户认证功能。
    包含用户的基本信息、认证信息和偏好设置。
    """
    __tablename__ = "accounts"
    __table_args__ = (db.PrimaryKeyConstraint("id", name="account_pkey"), db.Index("account_email_idx", "email"))

    id: Mapped[str] = mapped_column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    name = db.Column(db.String(255), nullable=False)            # 用户名称
    email = db.Column(db.String(255), nullable=False)           # 电子邮箱，用于登录和通知
    password = db.Column(db.String(255), nullable=True)         # 加密后的密码
    password_salt = db.Column(db.String(255), nullable=True)    # 密码盐，用于密码加密
    avatar = db.Column(db.String(255))                          # 头像URL
    interface_language = db.Column(db.String(255))              # 界面语言首选项
    interface_theme = db.Column(db.String(255))                 # 界面主题首选项
    timezone = db.Column(db.String(255))                        # 用户时区设置
    last_login_at = db.Column(db.DateTime)                      # 最后登录时间
    last_login_ip = db.Column(db.String(255))                   # 最后登录IP
    last_active_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 最后活动时间
    status = db.Column(db.String(16), nullable=False, server_default=db.text("'active'::character varying"))  # 账户状态
    initialized_at = db.Column(db.DateTime)                     # 账户初始化完成时间
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 更新时间

    @property
    def is_password_set(self):
        """
        检查账户是否已设置密码
        
        :return: 布尔值，True表示已设置密码
        """
        return self.password is not None

    @property
    def current_tenant(self):
        """
        获取当前用户选择的租户
        
        :return: 当前租户对象
        """
        # FIXME: fix the type error later, because the type is important maybe cause some bugs
        return self._current_tenant  # type: ignore

    @current_tenant.setter
    def current_tenant(self, value: "Tenant"):
        """
        设置当前租户，同时更新租户角色信息
        
        :param value: 要设置的租户对象
        """
        tenant = value
        ta = TenantAccountJoin.query.filter_by(tenant_id=tenant.id, account_id=self.id).first()
        if ta:
            tenant.current_role = ta.role
        else:
            tenant = None  # type: ignore

        self._current_tenant = tenant

    @property
    def current_tenant_id(self) -> str | None:
        """
        获取当前租户ID
        
        :return: 当前租户ID，如无则返回None
        """
        return self._current_tenant.id if self._current_tenant else None

    @current_tenant_id.setter
    def current_tenant_id(self, value: str):
        """
        通过租户ID设置当前租户
        
        :param value: 租户ID
        """
        try:
            tenant_account_join = (
                db.session.query(Tenant, TenantAccountJoin)
                .filter(Tenant.id == value)
                .filter(TenantAccountJoin.tenant_id == Tenant.id)
                .filter(TenantAccountJoin.account_id == self.id)
                .one_or_none()
            )

            if tenant_account_join:
                tenant, ta = tenant_account_join
                tenant.current_role = ta.role
            else:
                tenant = None
        except Exception:
            tenant = None

        self._current_tenant = tenant

    @property
    def current_role(self):
        """
        获取用户在当前租户中的角色
        
        :return: 角色字符串
        """
        return self._current_tenant.current_role

    def get_status(self) -> AccountStatus:
        """
        获取账户状态的枚举值
        
        :return: AccountStatus枚举对象
        """
        status_str = self.status
        return AccountStatus(status_str)

    @classmethod
    def get_by_openid(cls, provider: str, open_id: str):
        """
        通过第三方身份提供商和OpenID查找账户
        
        用于第三方登录功能，查找已关联的账户
        
        :param provider: 身份提供商标识
        :param open_id: 在提供商系统中的唯一ID
        :return: 账户对象，如不存在则返回None
        """
        account_integrate = (
            db.session.query(AccountIntegrate)
            .filter(AccountIntegrate.provider == provider, AccountIntegrate.open_id == open_id)
            .one_or_none()
        )
        if account_integrate:
            return db.session.query(Account).filter(Account.id == account_integrate.account_id).one_or_none()
        return None

    # check current_user.current_tenant.current_role in ['admin', 'owner']
    @property
    def is_admin_or_owner(self):
        """
        检查用户是否为管理员或所有者
        
        :return: 布尔值，True表示用户有管理权限
        """
        return TenantAccountRole.is_privileged_role(self._current_tenant.current_role)

    @property
    def is_admin(self):
        """
        检查用户是否为管理员
        
        :return: 布尔值，True表示用户是管理员
        """
        return TenantAccountRole.is_admin_role(self._current_tenant.current_role)

    @property
    def is_editor(self):
        """
        检查用户是否有编辑权限
        
        :return: 布尔值，True表示用户有编辑权限
        """
        return TenantAccountRole.is_editing_role(self._current_tenant.current_role)

    @property
    def is_dataset_editor(self):
        """
        检查用户是否有数据集编辑权限
        
        :return: 布尔值，True表示用户可以编辑数据集
        """
        return TenantAccountRole.is_dataset_edit_role(self._current_tenant.current_role)

    @property
    def is_dataset_operator(self):
        """
        检查用户是否为数据集操作员
        
        :return: 布尔值，True表示用户是数据集操作员
        """
        return self._current_tenant.current_role == TenantAccountRole.DATASET_OPERATOR


class TenantStatus(enum.StrEnum):
    """
    租户状态枚举
    
    定义租户可能的状态
    """
    NORMAL = "normal"    # 正常状态，租户可正常使用
    ARCHIVE = "archive"  # 归档状态，租户被禁用或暂停


class TenantAccountRole(enum.StrEnum):
    """
    租户账户角色枚举
    
    定义用户在租户中可能的角色和权限级别
    """
    OWNER = "owner"              # 所有者，拥有所有权限
    ADMIN = "admin"              # 管理员，拥有大部分管理权限
    EDITOR = "editor"            # 编辑者，可以创建和编辑内容
    NORMAL = "normal"            # 普通用户，基础使用权限
    DATASET_OPERATOR = "dataset_operator"  # 数据集操作员，专注于数据集管理

    @staticmethod
    def is_valid_role(role: str) -> bool:
        """
        检查角色是否有效
        
        :param role: 角色名称
        :return: 布尔值，表示角色是否有效
        """
        if not role:
            return False
        return role in {
            TenantAccountRole.OWNER,
            TenantAccountRole.ADMIN,
            TenantAccountRole.EDITOR,
            TenantAccountRole.NORMAL,
            TenantAccountRole.DATASET_OPERATOR,
        }

    @staticmethod
    def is_privileged_role(role: str) -> bool:
        """
        检查角色是否具有特权
        
        :param role: 角色名称
        :return: 布尔值，表示角色是否具有管理特权
        """
        if not role:
            return False
        return role in {TenantAccountRole.OWNER, TenantAccountRole.ADMIN}

    @staticmethod
    def is_admin_role(role: str) -> bool:
        """
        检查角色是否为管理员
        
        :param role: 角色名称
        :return: 布尔值，表示角色是否为管理员
        """
        if not role:
            return False
        return role == TenantAccountRole.ADMIN

    @staticmethod
    def is_non_owner_role(role: str) -> bool:
        """
        检查角色是否为非所有者角色
        
        :param role: 角色名称
        :return: 布尔值，表示角色是否为非所有者角色
        """
        if not role:
            return False
        return role in {
            TenantAccountRole.ADMIN,
            TenantAccountRole.EDITOR,
            TenantAccountRole.NORMAL,
            TenantAccountRole.DATASET_OPERATOR,
        }

    @staticmethod
    def is_editing_role(role: str) -> bool:
        """
        检查角色是否有编辑权限
        
        :param role: 角色名称
        :return: 布尔值，表示角色是否有编辑权限
        """
        if not role:
            return False
        return role in {TenantAccountRole.OWNER, TenantAccountRole.ADMIN, TenantAccountRole.EDITOR}

    @staticmethod
    def is_dataset_edit_role(role: str) -> bool:
        """
        检查角色是否有数据集编辑权限
        
        :param role: 角色名称
        :return: 布尔值，表示角色是否有数据集编辑权限
        """
        if not role:
            return False
        return role in {
            TenantAccountRole.OWNER,
            TenantAccountRole.ADMIN,
            TenantAccountRole.EDITOR,
            TenantAccountRole.DATASET_OPERATOR,
        }


class Tenant(db.Model):  # type: ignore[name-defined]
    """
    租户模型
    
    代表系统中的一个工作区或组织，包含多个用户和资源。
    租户是资源隔离的主要单位，不同租户的数据互相独立。
    """
    __tablename__ = "tenants"
    __table_args__ = (db.PrimaryKeyConstraint("id", name="tenant_pkey"),)

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    name = db.Column(db.String(255), nullable=False)    # 租户名称
    encrypt_public_key = db.Column(db.Text)             # 加密公钥，用于加密敏感数据
    plan = db.Column(db.String(255), nullable=False, server_default=db.text("'basic'::character varying"))
    status = db.Column(db.String(255), nullable=False, server_default=db.text("'normal'::character varying"))
    custom_config = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())

    def get_accounts(self) -> list[Account]:
        return (
            db.session.query(Account)
            .filter(Account.id == TenantAccountJoin.account_id, TenantAccountJoin.tenant_id == self.id)
            .all()
        )

    @property
    def custom_config_dict(self) -> dict:
        """
        获取自定义配置的字典形式
        
        :return: 配置字典
        """
        return json.loads(self.custom_config) if self.custom_config else {}

    @custom_config_dict.setter
    def custom_config_dict(self, value: dict):
        """
        设置自定义配置
        
        :param value: 配置字典
        """
        self.custom_config = json.dumps(value)


class TenantAccountJoin(db.Model):  # type: ignore[name-defined]
    """
    租户账户关联模型
    
    表示账户和租户之间的多对多关系，记录账户在租户中的角色和状态。
    """
    __tablename__ = "tenant_account_joins"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="tenant_account_join_pkey"),
        db.Index("tenant_account_join_account_id_idx", "account_id"),
        db.Index("tenant_account_join_tenant_id_idx", "tenant_id"),
        db.UniqueConstraint("tenant_id", "account_id", name="unique_tenant_account_join"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    tenant_id = db.Column(StringUUID, nullable=False)     # 租户ID
    account_id = db.Column(StringUUID, nullable=False)    # 账户ID
    current = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))  # 是否为当前选中租户
    role = db.Column(db.String(16), nullable=False, server_default="normal")  # 在租户中的角色
    invited_by = db.Column(StringUUID, nullable=True)     # 邀请人ID
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 更新时间


class AccountIntegrate(db.Model):  # type: ignore[name-defined]
    """
    账户集成模型
    
    存储账户与第三方身份提供商的集成信息，用于第三方登录。
    """
    __tablename__ = "account_integrates"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="account_integrate_pkey"),
        db.UniqueConstraint("account_id", "provider", name="unique_account_provider"),
        db.UniqueConstraint("provider", "open_id", name="unique_provider_open_id"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    account_id = db.Column(StringUUID, nullable=False)      # 关联的账户ID
    provider = db.Column(db.String(16), nullable=False)     # 提供商标识（如Google, GitHub等）
    open_id = db.Column(db.String(255), nullable=False)     # 在提供商系统中的唯一ID
    encrypted_token = db.Column(db.String(255), nullable=False)  # 加密的访问令牌
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())  # 更新时间


class InvitationCode(db.Model):  # type: ignore[name-defined]
    """
    邀请码模型
    
    用于邀请新用户加入系统的邀请码记录。
    """
    __tablename__ = "invitation_codes"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="invitation_code_pkey"),
        db.Index("invitation_codes_batch_idx", "batch"),
        db.Index("invitation_codes_code_idx", "code", "status"),
    )

    id = db.Column(db.Integer, nullable=False)           # 邀请码ID
    batch = db.Column(db.String(255), nullable=False)    # 批次标识，用于批量管理
    code = db.Column(db.String(32), nullable=False)      # 邀请码
    status = db.Column(db.String(16), nullable=False, server_default=db.text("'unused'::character varying"))  # 状态
    used_at = db.Column(db.DateTime)                     # 使用时间
    used_by_tenant_id = db.Column(StringUUID)            # 使用此邀请码的租户ID
    used_by_account_id = db.Column(StringUUID)           # 使用此邀请码的账户ID
    deprecated_at = db.Column(db.DateTime)               # 废弃时间
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))  # 创建时间


class TenantPluginPermission(Base):
    """
    租户插件权限模型
    
    控制租户内不同角色对插件的安装和调试权限。
    """
    class InstallPermission(enum.StrEnum):
        """
        插件安装权限枚举
        """
        EVERYONE = "everyone"    # 所有人都可以安装
        ADMINS = "admins"        # 只有管理员可以安装
        NOBODY = "noone"         # 禁止安装

    class DebugPermission(enum.StrEnum):
        """
        插件调试权限枚举
        """
        EVERYONE = "everyone"    # 所有人都可以调试
        ADMINS = "admins"        # 只有管理员可以调试
        NOBODY = "noone"         # 禁止调试

    __tablename__ = "account_plugin_permissions"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="account_plugin_permission_pkey"),
        db.UniqueConstraint("tenant_id", name="unique_tenant_plugin"),
    )

    id: Mapped[str] = mapped_column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    tenant_id: Mapped[str] = mapped_column(StringUUID, nullable=False)  # 租户ID
    install_permission: Mapped[InstallPermission] = mapped_column(
        db.String(16), nullable=False, server_default="everyone"  # 安装权限
    )
    debug_permission: Mapped[DebugPermission] = mapped_column(db.String(16), nullable=False, server_default="noone")  # 调试权限
