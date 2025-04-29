from configs import dify_config
from dify_app import DifyApp


def init_app(app: DifyApp):
    """
    设置应用密钥
    
    从配置中获取SECRET_KEY并设置到应用实例。
    密钥用于会话数据的安全加密、CSRF保护和其他需要加密的功能。
    在生产环境中应使用强随机值，并妥善保管。
    
    :param app: Flask应用实例
    """
    app.secret_key = dify_config.SECRET_KEY
