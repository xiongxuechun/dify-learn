from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# PostgreSQL索引命名约定
# 这些命名约定确保在数据库中创建的索引和约束具有统一的命名格式
# 这对于数据库迁移和维护非常重要
POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",         # 索引命名格式
    "uq": "%(table_name)s_%(column_0_name)s_key",  # 唯一约束命名格式
    "ck": "%(table_name)s_%(constraint_name)s_check",  # 检查约束命名格式
    "fk": "%(table_name)s_%(column_0_name)s_fkey",  # 外键约束命名格式
    "pk": "%(table_name)s_pkey",            # 主键命名格式
}

# 创建SQLAlchemy元数据对象，使用PostgreSQL命名约定
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
# 初始化SQLAlchemy实例，所有模型将使用这个实例访问数据库
db = SQLAlchemy(metadata=metadata)
