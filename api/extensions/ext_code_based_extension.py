from core.extension.extension import Extension
from dify_app import DifyApp


def init_app(app: DifyApp):
    """
    初始化基于代码的扩展系统
    
    初始化Dify的扩展系统，该系统允许通过代码方式扩展应用功能。
    扩展系统提供了插件化架构，支持动态加载和管理各种功能模块。
    
    :param app: Flask应用实例
    """
    code_based_extension.init()


# 创建扩展系统实例
code_based_extension = Extension()
