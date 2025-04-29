from enum import StrEnum


class CreatedByRole(StrEnum):
    """
    创建者角色枚举
    
    用于标识创建各种资源的用户角色类型
    """
    ACCOUNT = "account"    # 由账户（管理员/开发者）创建
    END_USER = "end_user"  # 由终端用户创建


class UserFrom(StrEnum):
    """
    用户来源枚举
    
    标识用户的来源类型
    """
    ACCOUNT = "account"     # 账户用户（系统内部用户）
    END_USER = "end-user"   # 终端用户（外部用户）


class WorkflowRunTriggeredFrom(StrEnum):
    """
    工作流运行触发来源枚举
    
    标识工作流运行的触发方式
    """
    DEBUGGING = "debugging"  # 从调试环境触发
    APP_RUN = "app-run"      # 从应用运行环境触发
