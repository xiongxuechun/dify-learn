from configs import dify_config
from dify_app import DifyApp


def init_app(app: DifyApp):
    """
    初始化蓝图和CORS设置
    
    注册应用的所有蓝图(路由模块)并配置跨域资源共享(CORS)。
    为不同的API端点设置不同的CORS策略，确保API安全性的同时提供必要的访问权限。
    
    :param app: Flask应用实例
    """
    # 导入蓝图模块
    from flask_cors import CORS  # type: ignore

    from controllers.console import bp as console_app_bp     # 控制台API蓝图
    from controllers.files import bp as files_bp             # 文件处理API蓝图  
    from controllers.inner_api import bp as inner_api_bp     # 内部API蓝图
    from controllers.service_api import bp as service_api_bp # 服务API蓝图
    from controllers.web import bp as web_bp                 # Web页面API蓝图

    # 配置服务API的CORS和注册蓝图
    CORS(
        service_api_bp,
        allow_headers=["Content-Type", "Authorization", "X-App-Code"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
    )
    app.register_blueprint(service_api_bp)

    # 配置Web API的CORS和注册蓝图
    CORS(
        web_bp,
        resources={r"/*": {"origins": dify_config.WEB_API_CORS_ALLOW_ORIGINS}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-App-Code"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        expose_headers=["X-Version", "X-Env"],
    )
    app.register_blueprint(web_bp)

    # 配置控制台API的CORS和注册蓝图
    CORS(
        console_app_bp,
        resources={r"/*": {"origins": dify_config.CONSOLE_CORS_ALLOW_ORIGINS}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        expose_headers=["X-Version", "X-Env"],
    )
    app.register_blueprint(console_app_bp)

    # 配置文件API的CORS和注册蓝图
    CORS(files_bp, allow_headers=["Content-Type"], methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"])
    app.register_blueprint(files_bp)

    # 注册内部API蓝图（无需CORS，因为仅内部访问）
    app.register_blueprint(inner_api_bp)
