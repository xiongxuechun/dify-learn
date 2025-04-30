from flask_restful import Resource  # type: ignore

from controllers.console import api


class PingApi(Resource):
    def get(self):
        """
        健康检查接口
        
        提供一个简单的健康检查端点，用于监控系统和负载均衡器确认API服务的可用性。
        返回"pong"表示API服务正常运行中。
        
        :return: 包含"pong"响应的JSON对象
        """
        return {"result": "pong"}


# 注册Ping API路由到"/ping"端点
api.add_resource(PingApi, "/ping")
