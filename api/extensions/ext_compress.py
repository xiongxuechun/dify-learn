from configs import dify_config
from dify_app import DifyApp


def is_enabled() -> bool:
    """
    检查响应压缩功能是否启用
    
    根据配置决定是否启用API响应压缩。
    压缩可以减少网络传输数据量，提高API性能。
    
    :return: 布尔值，表示压缩功能是否启用
    """
    return dify_config.API_COMPRESSION_ENABLED


def init_app(app: DifyApp):
    """
    初始化响应压缩扩展
    
    配置Flask-Compress扩展，用于自动压缩HTTP响应内容。
    当请求的客户端支持压缩时，会自动使用gzip或其他压缩算法。
    
    :param app: Flask应用实例
    """
    from flask_compress import Compress  # type: ignore

    compress = Compress()
    compress.init_app(app)
