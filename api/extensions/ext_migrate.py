from dify_app import DifyApp


def init_app(app: DifyApp):
    """
    初始化数据库迁移扩展
    
    配置Flask-Migrate扩展，用于管理数据库模式迁移。
    该扩展提供了'flask db'命令组，允许创建、应用和管理数据库迁移。
    依赖于数据库扩展(ext_database)已经被初始化。
    
    :param app: Flask应用实例
    """
    import flask_migrate  # type: ignore

    from extensions.ext_database import db

    flask_migrate.Migrate(app, db)
