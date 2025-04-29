from typing import Any, Union

import redis
from redis.cluster import ClusterNode, RedisCluster
from redis.connection import Connection, SSLConnection
from redis.sentinel import Sentinel

from configs import dify_config
from dify_app import DifyApp


class RedisClientWrapper:
    """
    A wrapper class for the Redis client that addresses the issue where the global
    `redis_client` variable cannot be updated when a new Redis instance is returned
    by Sentinel.

    This class allows for deferred initialization of the Redis client, enabling the
    client to be re-initialized with a new instance when necessary. This is particularly
    useful in scenarios where the Redis instance may change dynamically, such as during
    a failover in a Sentinel-managed Redis setup.

    Attributes:
        _client (redis.Redis): The actual Redis client instance. It remains None until
                               initialized with the `initialize` method.

    Methods:
        initialize(client): Initializes the Redis client if it hasn't been initialized already.
        __getattr__(item): Delegates attribute access to the Redis client, raising an error
                           if the client is not initialized.
                           
    Redis客户端包装类，解决了在哨兵模式下全局redis_client变量无法更新的问题。
    
    通过延迟初始化Redis客户端，允许在必要时（如哨兵故障转移）用新实例重新初始化客户端。
    这种设计使得Redis连接可以动态变化，提高系统的可用性和弹性。
    
    属性:
        _client (redis.Redis): 实际的Redis客户端实例。在调用`initialize`方法前为None。
        
    方法:
        initialize(client): 如果客户端尚未初始化，则初始化Redis客户端。
        __getattr__(item): 将属性访问委托给Redis客户端，若客户端未初始化则抛出错误。
    """

    def __init__(self):
        """
        初始化Redis客户端包装器，创建一个空的客户端引用
        """
        self._client = None

    def initialize(self, client):
        """
        初始化Redis客户端
        
        仅在客户端尚未初始化时设置客户端实例
        
        :param client: Redis客户端实例
        """
        if self._client is None:
            self._client = client

    def __getattr__(self, item):
        """
        代理属性访问到实际的Redis客户端
        
        如果客户端尚未初始化，则抛出运行时错误
        
        :param item: 要访问的属性名
        :return: Redis客户端的相应属性
        :raises RuntimeError: 当Redis客户端未初始化时
        """
        if self._client is None:
            raise RuntimeError("Redis客户端未初始化。请先调用init_app方法。")
        return getattr(self._client, item)


# 创建全局Redis客户端包装器实例
redis_client = RedisClientWrapper()


def init_app(app: DifyApp):
    """
    初始化Redis连接
    
    根据配置选择适当的Redis连接模式（标准/哨兵/集群）并初始化
    
    :param app: Flask应用实例
    """
    global redis_client

    # 根据配置决定使用普通连接还是SSL连接
    connection_class: type[Union[Connection, SSLConnection]] = Connection
    if dify_config.REDIS_USE_SSL:
        connection_class = SSLConnection

    # 基本Redis连接参数
    redis_params: dict[str, Any] = {
        "username": dify_config.REDIS_USERNAME,
        "password": dify_config.REDIS_PASSWORD or None,  # 临时修复空密码的问题
        "db": dify_config.REDIS_DB,
        "encoding": "utf-8",
        "encoding_errors": "strict",
        "decode_responses": False,
    }

    # 哨兵模式 - 用于高可用Redis部署
    if dify_config.REDIS_USE_SENTINEL:
        # 验证哨兵配置
        assert dify_config.REDIS_SENTINELS is not None, "启用哨兵模式时必须设置REDIS_SENTINELS"
        # 解析哨兵主机列表
        sentinel_hosts = [
            (node.split(":")[0], int(node.split(":")[1])) for node in dify_config.REDIS_SENTINELS.split(",")
        ]
        # 创建哨兵连接
        sentinel = Sentinel(
            sentinel_hosts,
            sentinel_kwargs={
                "socket_timeout": dify_config.REDIS_SENTINEL_SOCKET_TIMEOUT,
                "username": dify_config.REDIS_SENTINEL_USERNAME,
                "password": dify_config.REDIS_SENTINEL_PASSWORD,
            },
        )
        # 获取主节点连接
        master = sentinel.master_for(dify_config.REDIS_SENTINEL_SERVICE_NAME, **redis_params)
        redis_client.initialize(master)
    # 集群模式 - 用于分布式Redis部署
    elif dify_config.REDIS_USE_CLUSTERS:
        # 验证集群配置
        assert dify_config.REDIS_CLUSTERS is not None, "启用集群模式时必须设置REDIS_CLUSTERS"
        # 解析集群节点列表
        nodes = [
            ClusterNode(host=node.split(":")[0], port=int(node.split(":")[1]))
            for node in dify_config.REDIS_CLUSTERS.split(",")
        ]
        # FIXME: mypy error here, try to figure out how to fix it
        # 创建集群连接
        redis_client.initialize(RedisCluster(startup_nodes=nodes, password=dify_config.REDIS_CLUSTERS_PASSWORD))  # type: ignore
    # 标准模式 - 单节点Redis连接
    else:
        # 添加标准连接特有参数
        redis_params.update(
            {
                "host": dify_config.REDIS_HOST,
                "port": dify_config.REDIS_PORT,
                "connection_class": connection_class,
            }
        )
        # 创建连接池和客户端
        pool = redis.ConnectionPool(**redis_params)
        redis_client.initialize(redis.Redis(connection_pool=pool))

    # 将Redis客户端添加到应用扩展中
    app.extensions["redis"] = redis_client
