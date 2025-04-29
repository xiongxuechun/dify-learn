from dify_app import DifyApp


def init_app(app: DifyApp):
    """
    配置Python警告过滤器
    
    设置警告过滤规则，忽略ResourceWarning类型的警告。
    这类警告通常与资源管理相关，在生产环境中可能会产生大量无用日志。
    该设置可以减少日志噪音，提高日志可读性。
    
    :param app: Flask应用实例
    """
    import warnings

    warnings.simplefilter("ignore", ResourceWarning)
