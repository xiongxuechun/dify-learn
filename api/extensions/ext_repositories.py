"""
Extension for initializing repositories.

This extension registers repository implementations with the RepositoryFactory.

初始化数据仓库的扩展。

该扩展将仓库实现注册到仓库工厂中，使用依赖注入模式管理数据访问层。
"""

from dify_app import DifyApp
from repositories.repository_registry import register_repositories


def init_app(_app: DifyApp) -> None:
    """
    Initialize repository implementations.

    Args:
        _app: The Flask application instance (unused)
        
    初始化仓库实现
    
    使用仓库模式来分离数据访问逻辑和业务逻辑，提高代码可维护性和可测试性。
    仓库注册过程将具体的仓库实现类与抽象接口绑定，便于依赖注入。
    
    参数:
        _app: Flask应用实例(未使用)
    """
    register_repositories()
