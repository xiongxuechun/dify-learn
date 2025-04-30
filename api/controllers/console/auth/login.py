from typing import cast

import flask_login  # type: ignore
from flask import request
from flask_restful import Resource, reqparse  # type: ignore

import services
from configs import dify_config
from constants.languages import languages
from controllers.console import api
from controllers.console.auth.error import (
    EmailCodeError,
    EmailOrPasswordMismatchError,
    EmailPasswordLoginLimitError,
    InvalidEmailError,
    InvalidTokenError,
)
from controllers.console.error import (
    AccountBannedError,
    AccountInFreezeError,
    AccountNotFound,
    EmailSendIpLimitError,
    NotAllowedCreateWorkspace,
)
from controllers.console.wraps import email_password_login_enabled, setup_required
from events.tenant_event import tenant_was_created
from libs.helper import email, extract_remote_ip
from libs.password import valid_password
from models.account import Account
from services.account_service import AccountService, RegisterService, TenantService
from services.billing_service import BillingService
from services.errors.account import AccountRegisterError
from services.errors.workspace import WorkSpaceNotAllowedCreateError
from services.feature_service import FeatureService


class LoginApi(Resource):
    """
    用户登录API
    
    处理用户通过邮箱和密码进行身份验证和登录的请求。
    支持邀请链接登录、记住登录状态等功能。
    """

    @setup_required
    @email_password_login_enabled
    def post(self):
        """
        用户身份验证和登录处理
        
        接收用户提交的邮箱和密码，验证身份并生成访问令牌。
        支持邀请注册、语言设置和记住登录状态等功能。
        包含登录错误率限制，防止暴力破解攻击。
        
        :return: 登录成功返回token对，失败返回相应错误信息
        """
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=email, required=True, location="json")
        parser.add_argument("password", type=valid_password, required=True, location="json")
        parser.add_argument("remember_me", type=bool, required=False, default=False, location="json")
        parser.add_argument("invite_token", type=str, required=False, default=None, location="json")
        parser.add_argument("language", type=str, required=False, default="en-US", location="json")
        args = parser.parse_args()

        # 检查账户是否因计费原因被冻结
        if dify_config.BILLING_ENABLED and BillingService.is_email_in_freeze(args["email"]):
            raise AccountInFreezeError()

        # 检查登录错误率限制（防止暴力破解攻击）
        is_login_error_rate_limit = AccountService.is_login_error_rate_limit(args["email"])
        if is_login_error_rate_limit:
            raise EmailPasswordLoginLimitError()

        # 处理邀请令牌
        invitation = args["invite_token"]
        if invitation:
            invitation = RegisterService.get_invitation_if_token_valid(None, args["email"], invitation)

        # 设置用户界面语言偏好
        if args["language"] is not None and args["language"] == "zh-Hans":
            language = "zh-Hans"
        else:
            language = "en-US"

        try:
            # 根据邀请情况进行身份验证
            if invitation:
                data = invitation.get("data", {})
                invitee_email = data.get("email") if data else None
                if invitee_email != args["email"]:
                    raise InvalidEmailError()
                account = AccountService.authenticate(args["email"], args["password"], args["invite_token"])
            else:
                account = AccountService.authenticate(args["email"], args["password"])
        except services.errors.account.AccountLoginError:
            # 账户被禁用
            raise AccountBannedError()
        except services.errors.account.AccountPasswordError:
            # 密码错误，增加错误计数
            AccountService.add_login_error_rate_limit(args["email"])
            raise EmailOrPasswordMismatchError()
        except services.errors.account.AccountNotFoundError:
            # 账户不存在，如果允许注册则发送重置密码邮件
            if FeatureService.get_system_features().is_allow_register:
                token = AccountService.send_reset_password_email(email=args["email"], language=language)
                return {"result": "fail", "data": token, "code": "account_not_found"}
            else:
                raise AccountNotFound()
        
        # 检查用户是否加入了租户（工作区）
        # 自托管模式下只有一个工作区
        tenants = TenantService.get_join_tenants(account)
        if len(tenants) == 0:
            return {
                "result": "fail",
                "data": "workspace not found, please contact system admin to invite you to join in a workspace",
            }

        # 生成访问令牌并返回
        token_pair = AccountService.login(account=account, ip_address=extract_remote_ip(request))
        AccountService.reset_login_error_rate_limit(args["email"])
        return {"result": "success", "data": token_pair.model_dump()}


class LogoutApi(Resource):
    """
    用户登出API
    
    处理用户退出登录的请求，清除会话信息和令牌。
    """
    
    @setup_required
    def get(self):
        """
        处理用户登出请求
        
        清除用户会话和令牌信息，完成登出流程。
        对于未登录用户，直接返回成功。
        
        :return: 登出结果的JSON响应
        """
        account = cast(Account, flask_login.current_user)
        if isinstance(account, flask_login.AnonymousUserMixin):
            return {"result": "success"}
        AccountService.logout(account=account)
        flask_login.logout_user()
        return {"result": "success"}


class ResetPasswordSendEmailApi(Resource):
    """
    重置密码邮件发送API
    
    处理用户请求发送重置密码邮件的功能。
    """
    
    @setup_required
    @email_password_login_enabled
    def post(self):
        """
        发送重置密码邮件
        
        接收用户邮箱地址，发送包含重置密码链接的邮件。
        根据系统配置，支持现有用户重置密码和新用户注册。
        
        :return: 发送结果及令牌的JSON响应
        """
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=email, required=True, location="json")
        parser.add_argument("language", type=str, required=False, location="json")
        args = parser.parse_args()

        # 设置邮件语言
        if args["language"] is not None and args["language"] == "zh-Hans":
            language = "zh-Hans"
        else:
            language = "en-US"
        
        try:
            # 尝试通过邮箱查找用户
            account = AccountService.get_user_through_email(args["email"])
        except AccountRegisterError as are:
            raise AccountInFreezeError()
            
        # 根据用户是否存在及系统配置，发送相应邮件
        if account is None:
            if FeatureService.get_system_features().is_allow_register:
                token = AccountService.send_reset_password_email(email=args["email"], language=language)
            else:
                raise AccountNotFound()
        else:
            token = AccountService.send_reset_password_email(account=account, language=language)

        return {"result": "success", "data": token}


class EmailCodeLoginSendEmailApi(Resource):
    """
    邮箱验证码登录发送API
    
    处理用户请求发送邮箱验证码以进行登录的功能。
    """
    
    @setup_required
    def post(self):
        """
        发送邮箱验证码登录邮件
        
        接收用户邮箱地址，发送包含登录验证码的邮件。
        包含IP限制，防止滥用发送功能。
        
        :return: 发送结果及令牌的JSON响应
        """
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=email, required=True, location="json")
        parser.add_argument("language", type=str, required=False, location="json")
        args = parser.parse_args()

        # 检查IP限制，防止滥用发送功能
        ip_address = extract_remote_ip(request)
        if AccountService.is_email_send_ip_limit(ip_address):
            raise EmailSendIpLimitError()

        # 设置邮件语言
        if args["language"] is not None and args["language"] == "zh-Hans":
            language = "zh-Hans"
        else:
            language = "en-US"
            
        try:
            # 尝试通过邮箱查找用户
            account = AccountService.get_user_through_email(args["email"])
        except AccountRegisterError as are:
            raise AccountInFreezeError()

        # 根据用户是否存在及系统配置，发送相应邮件
        if account is None:
            if FeatureService.get_system_features().is_allow_register:
                token = AccountService.send_email_code_login_email(email=args["email"], language=language)
            else:
                raise AccountNotFound()
        else:
            token = AccountService.send_email_code_login_email(account=account, language=language)

        return {"result": "success", "data": token}


class EmailCodeLoginApi(Resource):
    """
    邮箱验证码登录API
    
    处理用户通过邮箱验证码进行登录的请求。
    支持新用户自动注册和工作区创建。
    """
    
    @setup_required
    def post(self):
        """
        处理邮箱验证码登录请求
        
        验证用户提交的邮箱验证码，完成登录或注册流程。
        支持创建工作区和自动登录功能。
        
        :return: 登录结果及令牌的JSON响应
        """
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str, required=True, location="json")
        parser.add_argument("code", type=str, required=True, location="json")
        parser.add_argument("token", type=str, required=True, location="json")
        args = parser.parse_args()

        user_email = args["email"]

        # 验证令牌有效性
        token_data = AccountService.get_email_code_login_data(args["token"])
        if token_data is None:
            raise InvalidTokenError()

        # 验证邮箱和验证码匹配
        if token_data["email"] != args["email"]:
            raise InvalidEmailError()

        if token_data["code"] != args["code"]:
            raise EmailCodeError()

        # 验证成功，撤销令牌防止重用
        AccountService.revoke_email_code_login_token(args["token"])
        
        try:
            # 获取用户信息
            account = AccountService.get_user_through_email(user_email)
        except AccountRegisterError as are:
            raise AccountInFreezeError()
            
        # 处理现有用户
        if account:
            tenant = TenantService.get_join_tenants(account)
            if not tenant:
                # 用户没有工作区，尝试创建
                if not FeatureService.get_system_features().is_allow_create_workspace:
                    raise NotAllowedCreateWorkspace()
                else:
                    # 创建工作区并将用户设为所有者
                    tenant = TenantService.create_tenant(f"{account.name}'s Workspace")
                    TenantService.create_tenant_member(tenant, account, role="owner")
                    account.current_tenant = tenant
                    tenant_was_created.send(tenant)

        # 处理新用户注册
        if account is None:
            try:
                # 创建新账户和工作区
                account = AccountService.create_account_and_tenant(
                    email=user_email, name=user_email, interface_language=languages[0]
                )
            except WorkSpaceNotAllowedCreateError:
                return NotAllowedCreateWorkspace()
            except AccountRegisterError as are:
                raise AccountInFreezeError()
                
        # 生成登录令牌并返回
        token_pair = AccountService.login(account, ip_address=extract_remote_ip(request))
        AccountService.reset_login_error_rate_limit(args["email"])
        return {"result": "success", "data": token_pair.model_dump()}


class RefreshTokenApi(Resource):
    """
    刷新令牌API
    
    处理用户刷新访问令牌的请求，用于延长会话时间。
    """
    
    def post(self):
        """
        刷新访问令牌
        
        接收刷新令牌，验证其有效性并生成新的令牌对。
        如果刷新令牌无效或过期，返回401错误。
        
        :return: 新的令牌对或错误信息
        """
        parser = reqparse.RequestParser()
        parser.add_argument("refresh_token", type=str, required=True, location="json")
        args = parser.parse_args()

        try:
            # 使用刷新令牌生成新的访问令牌对
            new_token_pair = AccountService.refresh_token(args["refresh_token"])
            return {"result": "success", "data": new_token_pair.model_dump()}
        except Exception as e:
            # 刷新失败，可能是令牌无效或过期
            return {"result": "fail", "data": str(e)}, 401


# 注册API路由
api.add_resource(LoginApi, "/login")
api.add_resource(LogoutApi, "/logout")
api.add_resource(EmailCodeLoginSendEmailApi, "/email-code-login")
api.add_resource(EmailCodeLoginApi, "/email-code-login/validity")
api.add_resource(ResetPasswordSendEmailApi, "/reset-password")
api.add_resource(RefreshTokenApi, "/refresh-token")
