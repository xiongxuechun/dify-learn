from sqlalchemy.orm import declarative_base

from models.engine import metadata

# 创建SQLAlchemy ORM基类
# 所有数据库模型都将继承这个基类
# 使用共享的元数据对象，确保所有模型使用同一个数据库连接
Base = declarative_base(metadata=metadata)
