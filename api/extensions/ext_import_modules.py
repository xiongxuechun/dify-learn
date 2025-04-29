from dify_app import DifyApp


def init_app(app: DifyApp):
    """
    导入必要的模块和组件
    
    导入应用中需要预先加载的各种模块，确保它们在应用启动时被初始化。
    这里导入了事件处理器，以便注册到事件系统中。
    noqa标记用于抑制未使用导入的代码检查警告。
    
    :param app: Flask应用实例
    """
    from events import event_handlers  # noqa: F401
