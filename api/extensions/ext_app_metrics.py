import json
import os
import threading

from flask import Response

from configs import dify_config
from dify_app import DifyApp


def init_app(app: DifyApp):
    """
    初始化应用指标监控
    
    配置健康检查、线程监控和数据库连接池统计等指标监控端点。
    这些端点对系统运维和监控非常重要，可以用于负载均衡健康检查和性能监控。
    
    :param app: Flask应用实例
    """
    @app.after_request
    def after_request(response):
        """
        请求后处理，添加版本和环境信息到响应头
        
        :param response: Flask响应对象
        :return: 添加了版本信息的响应对象
        """
        response.headers.add("X-Version", dify_config.CURRENT_VERSION)
        response.headers.add("X-Env", dify_config.DEPLOY_ENV)
        return response

    @app.route("/health")
    def health():
        """
        健康检查端点
        
        返回应用当前状态、进程ID和版本信息。
        该端点用于负载均衡器检查应用是否正常运行。
        
        :return: 包含健康状态的JSON响应
        """
        return Response(
            json.dumps({"pid": os.getpid(), "status": "ok", "version": dify_config.CURRENT_VERSION}),
            status=200,
            content_type="application/json",
        )

    @app.route("/threads")
    def threads():
        """
        线程监控端点
        
        返回当前活跃的线程数量和详细信息。
        用于监控应用的线程使用情况，排查可能的线程泄漏问题。
        
        :return: 包含线程信息的JSON响应
        """
        num_threads = threading.active_count()
        threads = threading.enumerate()

        thread_list = []
        for thread in threads:
            thread_name = thread.name
            thread_id = thread.ident
            is_alive = thread.is_alive()

            thread_list.append(
                {
                    "name": thread_name,
                    "id": thread_id,
                    "is_alive": is_alive,
                }
            )

        return {
            "pid": os.getpid(),
            "thread_num": num_threads,
            "threads": thread_list,
        }

    @app.route("/db-pool-stat")
    def pool_stat():
        """
        数据库连接池统计端点
        
        返回SQLAlchemy数据库连接池的统计信息。
        用于监控数据库连接使用情况，及时发现连接泄漏或配置问题。
        
        :return: 包含连接池统计信息的JSON响应
        """
        from extensions.ext_database import db

        engine = db.engine
        # TODO: 修复类型错误
        # FIXME 可能是sqlalchemy的问题
        return {
            "pid": os.getpid(),
            "pool_size": engine.pool.size(),  # type: ignore
            "checked_in_connections": engine.pool.checkedin(),  # type: ignore
            "checked_out_connections": engine.pool.checkedout(),  # type: ignore
            "overflow_connections": engine.pool.overflow(),  # type: ignore
            "connection_timeout": engine.pool.timeout(),  # type: ignore
            "recycle_time": db.engine.pool._recycle,  # type: ignore
        }
