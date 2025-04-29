import json

import flask_login  # type: ignore
from flask import Response, request
from flask_login import user_loaded_from_request, user_logged_in
from werkzeug.exceptions import Unauthorized

import contexts
from dify_app import DifyApp
from libs.passport import PassportService
from services.account_service import AccountService

# 创建登录管理器实例
login_manager = flask_login.LoginManager()


# Flask-Login配置
@login_manager.request_loader
def load_user_from_request(request_from_flask_login):
    """
    根据请求加载用户
    
    从HTTP请求中提取认证令牌，验证其有效性，并加载对应的用户账户。
    支持从Authorization头或URL参数中获取令牌。
    
    :param request_from_flask_login: Flask-Login传递的请求对象
    :return: 已认证的用户对象或None
    :raises Unauthorized: 当认证令牌无效或格式错误时
    """
    # 只处理控制台和内部API的请求
    if request.blueprint not in {"console", "inner_api"}:
        return None
        
    # 从请求头或URL参数中获取认证令牌
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        auth_token = request.args.get("_token")
        if not auth_token:
            raise Unauthorized("Invalid Authorization token.")
    else:
        # 验证Authorization头格式
        if " " not in auth_header:
            raise Unauthorized("Invalid Authorization header format. Expected 'Bearer <api-key>' format.")
        auth_scheme, auth_token = auth_header.split(None, 1)
        auth_scheme = auth_scheme.lower()
        if auth_scheme != "bearer":
            raise Unauthorized("Invalid Authorization header format. Expected 'Bearer <api-key>' format.")

    # 验证令牌并获取用户ID
    decoded = PassportService().verify(auth_token)
    user_id = decoded.get("user_id")

    # 加载用户账户信息
    logged_in_account = AccountService.load_logged_in_account(account_id=user_id)
    return logged_in_account


@user_logged_in.connect
@user_loaded_from_request.connect
def on_user_logged_in(_sender, user):
    """
    用户登录后的回调函数
    
    当用户登录或从请求中加载后，设置当前租户ID到上下文中。
    这确保了后续操作能正确识别用户所属的租户。
    
    :param _sender: 发送信号的对象
    :param user: 登录用户对象
    """
    if user:
        contexts.tenant_id.set(user.current_tenant_id)


@login_manager.unauthorized_handler
def unauthorized_handler():
    """
    处理未授权请求
    
    当用户未登录或认证失败时，返回401状态码和JSON格式的错误信息。
    
    :return: 401状态的JSON响应
    """
    return Response(
        json.dumps({"code": "unauthorized", "message": "Unauthorized."}),
        status=401,
        content_type="application/json",
    )


def init_app(app: DifyApp):
    """
    初始化用户登录扩展
    
    将登录管理器与Flask应用关联，启用用户认证功能。
    
    :param app: Flask应用实例
    """
    login_manager.init_app(app)
