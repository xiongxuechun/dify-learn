"""
应用程序入口文件

此文件是整个Flask应用的入口点，负责：
1. 判断当前运行环境（数据库迁移或正常运行）
2. 根据环境配置gevent和其他性能优化
3. 创建并配置Flask应用实例
"""

import os
import sys


def is_db_command():
    """
    检查当前是否为数据库迁移命令
    
    通过检查命令行参数判断当前执行的是否是Flask数据库迁移相关命令。
    这样可以在数据库迁移时只加载必要的组件，提高效率。
    
    :return: True 如果命令以'flask db'开头，表示是数据库迁移命令；否则返回 False
    """
    if len(sys.argv) > 1 and sys.argv[0].endswith("flask") and sys.argv[1] == "db":
        return True
    return False


# 根据运行环境创建应用实例
if is_db_command():
    # 数据库迁移模式：
    # 仅初始化与数据库迁移相关的必要组件，避免加载其他不必要的扩展
    from app_factory import create_migrations_app

    app = create_migrations_app()
else:
    # 正常应用模式：
    # 根据调试状态决定是否启用gevent优化
    
    # 检查是否处于调试模式
    # JetBrains IDE的Python调试器与gevent存在兼容性问题
    # 注意：如果使用debugpy并设置GEVENT_SUPPORT=True，则可以在调试模式下使用gevent
    if (flask_debug := os.environ.get("FLASK_DEBUG", "0")) and flask_debug.lower() in {"false", "0", "no"}:
        # 非调试模式：启用gevent优化以提升性能
        
        # 1. 应用gevent monkey patch
        # 将Python标准库中的阻塞操作替换为gevent的非阻塞版本
        from gevent import monkey  # type: ignore
        monkey.patch_all()

        # 2. 为gRPC启用gevent支持
        # 使gRPC能够在gevent环境中正常工作
        from grpc.experimental import gevent as grpc_gevent  # type: ignore
        grpc_gevent.init_gevent()

        # 3. 为PostgreSQL驱动启用gevent支持
        # 使psycopg在gevent环境中能够异步工作
        import psycogreen.gevent  # type: ignore
        psycogreen.gevent.patch_psycopg()

    # 创建完整的应用实例
    from app_factory import create_app

    app = create_app()
    # 获取Celery实例，用于处理异步任务
    celery = app.extensions["celery"]

# 开发环境直接运行入口
if __name__ == "__main__":
    # 启动开发服务器
    # host="0.0.0.0" 表示监听所有网络接口
    # port=5001 指定服务端口
    app.run(host="0.0.0.0", port=5001)
