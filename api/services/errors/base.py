"""
服务层错误处理基础模块

此模块定义了服务层错误处理的基础类，所有具体的服务错误类都应该继承自这个基类。
"""

from typing import Optional


class BaseServiceError(ValueError):
    """
    服务层错误基类
    
    所有服务层相关的错误都应该继承自这个基类。
    它继承自ValueError，并添加了可选的错误描述字段。
    
    属性:
        description (Optional[str]): 错误的详细描述信息，可以为空
    """
    def __init__(self, description: Optional[str] = None):
        """
        初始化服务错误
        
        Args:
            description (Optional[str]): 错误的详细描述信息，可以为空
        """
        self.description = description
