from sqlalchemy import CHAR, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID


class StringUUID(TypeDecorator):
    """
    字符串UUID类型
    
    自定义SQLAlchemy类型，用于处理UUID字段。
    在PostgreSQL中使用原生UUID类型，在其他数据库中使用CHAR(36)。
    确保UUID在不同数据库间的一致性处理。
    """
    impl = CHAR  # 底层实现类型
    cache_ok = True  # 表示此类型可以安全缓存

    def process_bind_param(self, value, dialect):
        """
        处理绑定参数（写入数据库前的转换）
        
        :param value: 输入值
        :param dialect: 数据库方言
        :return: 处理后的值
        """
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)  # PostgreSQL需要字符串形式的UUID
        else:
            return value.hex  # 其他数据库使用十六进制表示

    def load_dialect_impl(self, dialect):
        """
        加载特定数据库方言的实现
        
        :param dialect: 数据库方言
        :return: 方言特定的类型描述符
        """
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())  # PostgreSQL使用原生UUID类型
        else:
            return dialect.type_descriptor(CHAR(36))  # 其他数据库使用固定长度字符串

    def process_result_value(self, value, dialect):
        """
        处理结果值（从数据库读取后的转换）
        
        :param value: 数据库返回的值
        :param dialect: 数据库方言
        :return: 处理后的值
        """
        if value is None:
            return value
        return str(value)  # 总是返回字符串形式的UUID
