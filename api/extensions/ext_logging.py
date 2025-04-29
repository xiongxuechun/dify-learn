import logging
import os
import sys
import uuid
from logging.handlers import RotatingFileHandler

import flask

from configs import dify_config
from dify_app import DifyApp


def init_app(app: DifyApp):
    """
    初始化日志系统
    
    配置应用的日志处理器，包括文件日志和控制台日志，
    并设置日志格式、级别和时区等。
    
    :param app: Flask应用实例
    """
    log_handlers: list[logging.Handler] = []
    log_file = dify_config.LOG_FILE
    if log_file:
        # 如果配置了日志文件，创建文件日志处理器
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        log_handlers.append(
            RotatingFileHandler(
                filename=log_file,
                maxBytes=dify_config.LOG_FILE_MAX_SIZE * 1024 * 1024,  # 最大文件大小
                backupCount=dify_config.LOG_FILE_BACKUP_COUNT,         # 保留的日志文件数量
            )
        )

    # 始终添加标准输出处理器，确保日志同时输出到控制台
    sh = logging.StreamHandler(sys.stdout)
    log_handlers.append(sh)

    # 为所有处理器添加请求ID过滤器，使日志中包含请求ID
    for handler in log_handlers:
        handler.addFilter(RequestIdFilter())

    # 配置基本日志设置
    logging.basicConfig(
        level=dify_config.LOG_LEVEL,           # 日志级别
        format=dify_config.LOG_FORMAT,         # 日志格式
        datefmt=dify_config.LOG_DATEFORMAT,    # 日期格式
        handlers=log_handlers,                 # 处理器列表
        force=True,                            # 强制覆盖已存在的日志配置
    )
    # 禁用一些嘈杂日志的传播，避免重复日志记录
    logging.getLogger("sqlalchemy.engine").propagate = False
    
    # 配置日志时区
    log_tz = dify_config.LOG_TZ
    if log_tz:
        from datetime import datetime
        import pytz

        # 获取指定的时区
        timezone = pytz.timezone(log_tz)

        # 自定义时间转换函数，将日志时间戳转换为指定时区的时间
        def time_converter(seconds):
            return datetime.fromtimestamp(seconds, tz=timezone).timetuple()

        # 为所有处理器的格式化器应用时间转换函数
        for handler in logging.root.handlers:
            if handler.formatter:
                handler.formatter.converter = time_converter


def get_request_id():
    """
    获取当前请求的唯一标识符
    
    如果当前请求已有ID，则返回现有ID；
    否则生成一个新的UUID作为请求ID。
    
    :return: 请求ID字符串
    """
    if getattr(flask.g, "request_id", None):
        return flask.g.request_id

    # 生成新的请求ID（UUID的前10个字符）
    new_uuid = uuid.uuid4().hex[:10]
    flask.g.request_id = new_uuid

    return new_uuid


class RequestIdFilter(logging.Filter):
    """
    请求ID过滤器
    
    一个日志过滤器，使请求ID可以在日志格式中使用。
    检查是否在请求上下文中，因为在Flask完全加载前也可能需要记录日志。
    
    方法:
        filter(record): 将请求ID添加到日志记录中
    """
    def filter(self, record):
        """
        过滤日志记录
        
        将请求ID添加到日志记录对象中，如果不在请求上下文中则使用空字符串
        
        :param record: 日志记录对象
        :return: 始终返回True，表示日志记录应该被处理
        """
        record.req_id = get_request_id() if flask.has_request_context() else ""
        return True
