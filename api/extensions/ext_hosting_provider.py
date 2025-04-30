from core.hosting_configuration import HostingConfiguration
from dify_app import DifyApp

# 创建托管配置实例
hosting_configuration = HostingConfiguration()


def init_app(app: DifyApp):
    """
    初始化托管服务提供商配置
    
    设置应用的托管环境配置，根据不同的托管服务提供商(如AWS、Azure、GCP等)
    调整应用的行为和优化参数，确保应用能够在特定的托管环境中高效运行。
    
    :param app: Flask应用实例
    """
    hosting_configuration.init_app(app)
