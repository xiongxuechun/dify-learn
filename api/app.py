import os
import sys


def is_db_command():
    """
    检查当前是否为数据库迁移命令
    如果命令行参数为'flask db'开头，则判定为数据库相关命令
    
    :return: True 如果是数据库命令，否则 False
    """
    if len(sys.argv) > 1 and sys.argv[0].endswith("flask") and sys.argv[1] == "db":
        return True
    return False


# 创建应用实例
if is_db_command():
    # 如果是数据库迁移命令，只初始化必要的数据库相关扩展
    from app_factory import create_migrations_app

    app = create_migrations_app()
else:
    # 正常启动应用
    # JetBrains Python调试器与gevent配合不佳，因此在调试模式下禁用gevent
    # 如果使用debugpy并设置GEVENT_SUPPORT=True，则可以使用gevent进行调试
    if (flask_debug := os.environ.get("FLASK_DEBUG", "0")) and flask_debug.lower() in {"false", "0", "no"}:
        # 非调试模式下，应用gevent补丁以提高并发性能
        from gevent import monkey  # type: ignore

        # 应用gevent补丁，将阻塞操作替换为非阻塞版本
        monkey.patch_all()

        # 为gRPC应用gevent支持
        from grpc.experimental import gevent as grpc_gevent  # type: ignore
        grpc_gevent.init_gevent()

        # 为PostgreSQL驱动应用gevent补丁
        import psycogreen.gevent  # type: ignore
        psycogreen.gevent.patch_psycopg()

    # 导入并创建完整应用
    from app_factory import create_app

    app = create_app()
    # 获取Celery实例（用于异步任务处理）
    celery = app.extensions["celery"]

# 直接运行此文件时的启动入口
if __name__ == "__main__":
    # 在本地开发环境直接运行应用，监听所有网络接口，端口5001
    app.run(host="0.0.0.0", port=5001)
