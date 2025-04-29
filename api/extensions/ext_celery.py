from datetime import timedelta

import pytz
from celery import Celery, Task  # type: ignore
from celery.schedules import crontab  # type: ignore

from configs import dify_config
from dify_app import DifyApp


def init_app(app: DifyApp) -> Celery:
    """
    初始化Celery异步任务处理
    
    配置Celery，用于处理后台任务和定时任务。
    设置Celery的消息代理、结果后端、任务导入和定时任务计划。
    
    :param app: Flask应用实例
    :return: 配置好的Celery实例
    """
    class FlaskTask(Task):
        """
        Flask上下文感知的Celery任务类
        
        确保Celery任务在执行时拥有正确的Flask应用上下文，
        使任务内可以访问Flask的request、session等对象。
        """
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    # Redis Sentinel配置选项
    broker_transport_options = {}

    if dify_config.CELERY_USE_SENTINEL:
        broker_transport_options = {
            "master_name": dify_config.CELERY_SENTINEL_MASTER_NAME,
            "sentinel_kwargs": {
                "socket_timeout": dify_config.CELERY_SENTINEL_SOCKET_TIMEOUT,
            },
        }

    # 创建Celery实例
    celery_app = Celery(
        app.name,
        task_cls=FlaskTask,
        broker=dify_config.CELERY_BROKER_URL,
        backend=dify_config.CELERY_BACKEND,
        task_ignore_result=True,
    )

    # 添加SSL选项到Celery配置
    ssl_options = {
        "ssl_cert_reqs": None,
        "ssl_ca_certs": None,
        "ssl_certfile": None,
        "ssl_keyfile": None,
    }

    # 更新Celery配置
    celery_app.conf.update(
        result_backend=dify_config.CELERY_RESULT_BACKEND,
        broker_transport_options=broker_transport_options,
        broker_connection_retry_on_startup=True,
        worker_log_format=dify_config.LOG_FORMAT,
        worker_task_log_format=dify_config.LOG_FORMAT,
        worker_hijack_root_logger=False,
        timezone=pytz.timezone(dify_config.LOG_TZ or "UTC"),
    )

    # 如果启用了SSL，添加SSL配置
    if dify_config.BROKER_USE_SSL:
        celery_app.conf.update(
            broker_use_ssl=ssl_options,  # 添加SSL选项到代理配置
        )

    # 如果配置了日志文件，设置worker日志文件路径
    if dify_config.LOG_FILE:
        celery_app.conf.update(
            worker_logfile=dify_config.LOG_FILE,
        )

    # 设置为默认Celery实例并添加到Flask应用扩展中
    celery_app.set_default()
    app.extensions["celery"] = celery_app

    # 需要导入的任务模块
    imports = [
        "schedule.clean_embedding_cache_task",      # 清理嵌入缓存任务
        "schedule.clean_unused_datasets_task",      # 清理未使用数据集任务
        "schedule.create_tidb_serverless_task",     # 创建TiDB Serverless任务
        "schedule.update_tidb_serverless_status_task", # 更新TiDB Serverless状态任务
        "schedule.clean_messages",                  # 清理消息任务
        "schedule.mail_clean_document_notify_task", # 邮件清理文档通知任务
    ]
    
    # 定时任务执行间隔（天）
    day = dify_config.CELERY_BEAT_SCHEDULER_TIME
    
    # 定时任务计划配置
    beat_schedule = {
        "clean_embedding_cache_task": {
            "task": "schedule.clean_embedding_cache_task.clean_embedding_cache_task",
            "schedule": timedelta(days=day),
        },
        "clean_unused_datasets_task": {
            "task": "schedule.clean_unused_datasets_task.clean_unused_datasets_task",
            "schedule": timedelta(days=day),
        },
        "create_tidb_serverless_task": {
            "task": "schedule.create_tidb_serverless_task.create_tidb_serverless_task",
            "schedule": crontab(minute="0", hour="*"),  # 每小时执行一次
        },
        "update_tidb_serverless_status_task": {
            "task": "schedule.update_tidb_serverless_status_task.update_tidb_serverless_status_task",
            "schedule": timedelta(minutes=10),  # 每10分钟执行一次
        },
        "clean_messages": {
            "task": "schedule.clean_messages.clean_messages",
            "schedule": timedelta(days=day),
        },
        # 每周一执行
        "mail_clean_document_notify_task": {
            "task": "schedule.mail_clean_document_notify_task.mail_clean_document_notify_task",
            "schedule": crontab(minute="0", hour="10", day_of_week="1"),  # 每周一上午10点
        },
    }
    
    # 更新Celery配置，添加定时任务计划和导入列表
    celery_app.conf.update(beat_schedule=beat_schedule, imports=imports)

    return celery_app
