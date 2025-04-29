import os
import time

from configs import dify_config
from dify_app import DifyApp


def init_app(app: DifyApp):
    """
    初始化时区设置
    
    设置应用的默认时区，影响所有时间相关的操作。
    这是在应用启动时最先加载的扩展之一，确保其他扩展能使用正确的时区。
    
    :param app: Flask应用实例
    """
    os.environ["TZ"] = "UTC"
    # windows platform not support tzset
    if hasattr(time, "tzset"):
        time.tzset()
