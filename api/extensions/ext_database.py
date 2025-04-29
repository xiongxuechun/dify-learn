from dify_app import DifyApp
from models import db


def init_app(app: DifyApp):
    """
    初始化数据库连接
    
    为Flask应用配置SQLAlchemy数据库连接。
    该扩展是应用的核心扩展之一，提供ORM功能和数据库访问能力。
    数据库配置参数从应用配置中读取。
    
    :param app: Flask应用实例
    """
    db.init_app(app)
