from configs import dify_config
from dify_app import DifyApp


def init_app(app: DifyApp):
    """
    配置代理头信息修复
    
    在应用运行在反向代理(如Nginx、Apache)后面时,
    配置应用正确处理X-Forwarded-*头信息，确保能获取到正确的客户端IP地址、
    协议和端口信息。这对于安全审计和访问控制非常重要。
    
    :param app: Flask应用实例
    """
    if dify_config.RESPECT_XFORWARD_HEADERS_ENABLED:
        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(app.wsgi_app, x_port=1)  # type: ignore
