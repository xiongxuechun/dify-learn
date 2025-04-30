"""
应用工厂模块

此模块负责创建和配置Flask应用实例。采用工厂模式的主要优势：
1. 实现关注点分离，使应用的创建过程更加模块化
2. 便于测试，可以为不同场景创建不同配置的应用实例
3. 支持多实例部署，每个实例可以有自己的配置
4. 便于管理复杂的初始化过程和扩展依赖

主要功能：
- 创建基础Flask应用并加载配置
- 初始化各种Flask扩展
- 提供专用的数据库迁移应用创建功能
"""

import logging
import time

from configs import dify_config
from contexts.wrapper import RecyclableContextVar
from dify_app import DifyApp


# ----------------------------
# 应用工厂函数 - 实现关注点分离和测试便利性
# ----------------------------
def create_flask_app_with_configs() -> DifyApp:
    """
    创建基础Flask应用并加载配置
    
    创建一个原始的Flask应用(DifyApp)实例，并从配置文件加载设置。
    这一步骤不初始化任何扩展，只创建最基础的应用框架。
    
    主要步骤：
    1. 创建DifyApp实例
    2. 从配置对象加载设置
    3. 添加请求前处理钩子，确保请求上下文安全
    
    :return: 配置加载完成的DifyApp实例
    """
    dify_app = DifyApp(__name__)
    dify_app.config.from_mapping(dify_config.model_dump())

    # 添加请求前钩子
    @dify_app.before_request
    def before_request():
        # 为每个请求添加唯一标识符，支持线程重用和上下文安全
        # 这确保在高并发环境下请求上下文不会混淆
        # 特别重要：在使用线程池或协程池时防止上下文泄漏
        RecyclableContextVar.increment_thread_recycles()

    return dify_app


def create_app() -> DifyApp:
    """
    创建完整的应用实例
    
    这是主要的应用工厂函数，创建并初始化完整的应用，包括所有必要的扩展和配置。
    
    主要步骤：
    1. 记录开始时间（用于性能分析）
    2. 创建基础应用实例
    3. 初始化所有必要的扩展
    4. 在调试模式下记录创建过程的耗时
    
    :return: 完全初始化的应用实例
    """
    start_time = time.perf_counter()
    # 创建基础应用
    app = create_flask_app_with_configs()
    # 初始化所有扩展
    initialize_extensions(app)
    end_time = time.perf_counter()
    # 在调试模式下记录应用创建耗时
    if dify_config.DEBUG:
        logging.info(f"Finished create_app ({round((end_time - start_time) * 1000, 2)} ms)")
    return app


def initialize_extensions(app: DifyApp):
    """
    初始化所有应用扩展
    
    按照特定顺序初始化所有Flask扩展，确保依赖关系正确。
    每个扩展初始化都会被计时，并可选择性地启用或禁用。
    
    扩展初始化顺序的重要性：
    1. 基础设施扩展最先初始化（时区、日志等）
    2. 数据存储相关扩展其次（数据库、Redis等）
    3. 功能性扩展再次（登录、邮件等）
    4. 路由和命令行扩展最后
    5. 监控相关扩展最终（确保能够监控到其他所有组件）
    
    :param app: 待初始化扩展的应用实例
    """
    from extensions import (
        ext_app_metrics,  # 应用指标监控
        ext_blueprints,  # 蓝图/路由注册
        ext_celery,  # Celery异步任务
        ext_code_based_extension,  # 基于代码的扩展
        ext_commands,  # Flask命令行
        ext_compress,  # 响应压缩
        ext_database,  # 数据库连接
        ext_hosting_provider,  # 托管服务提供商
        ext_import_modules,  # 模块导入
        ext_logging,  # 日志配置
        ext_login,  # 用户登录
        ext_mail,  # 电子邮件
        ext_migrate,  # 数据库迁移
        ext_otel,  # OpenTelemetry监控
        ext_otel_patch,  # OpenTelemetry补丁
        ext_proxy_fix,  # 代理修复
        ext_redis,  # Redis缓存
        ext_repositories,  # 数据仓库
        ext_sentry,  # Sentry错误跟踪
        ext_set_secretkey,  # 密钥设置
        ext_storage,  # 文件存储
        ext_timezone,  # 时区设置
        ext_warnings,  # 警告处理
    )

    # 扩展初始化顺序，确保依赖正确
    extensions = [
        ext_timezone,           # 首先设置时区
        ext_logging,            # 然后配置日志
        ext_warnings,           # 设置警告处理
        ext_import_modules,     # 导入必要模块
        ext_set_secretkey,      # 设置密钥
        ext_compress,           # 设置响应压缩
        ext_code_based_extension, # 基于代码的扩展
        ext_database,           # 数据库初始化
        ext_app_metrics,        # 应用指标
        ext_migrate,            # 数据库迁移工具
        ext_redis,              # Redis缓存
        ext_storage,            # 文件存储
        ext_repositories,       # 数据仓库模式
        ext_celery,             # Celery异步任务
        ext_login,              # 用户登录
        ext_mail,               # 电子邮件
        ext_hosting_provider,   # 托管服务提供商
        ext_sentry,             # Sentry错误跟踪
        ext_proxy_fix,          # 代理修复
        ext_blueprints,         # 蓝图/路由注册（必须在所有其他扩展之后）
        ext_commands,           # Flask命令行
        ext_otel_patch,         # 在初始化OpenTelemetry之前应用补丁
        ext_otel,               # OpenTelemetry监控（最后初始化）
    ]
    
    # 逐个初始化扩展
    for ext in extensions:
        short_name = ext.__name__.split(".")[-1]
        # 检查扩展是否启用
        is_enabled = ext.is_enabled() if hasattr(ext, "is_enabled") else True
        if not is_enabled:
            if dify_config.DEBUG:
                logging.info(f"Skipped {short_name}")
            continue

        # 计时并初始化扩展
        start_time = time.perf_counter()
        ext.init_app(app)
        end_time = time.perf_counter()
        if dify_config.DEBUG:
            logging.info(f"Loaded {short_name} ({round((end_time - start_time) * 1000, 2)} ms)")


def create_migrations_app():
    """
    创建仅用于数据库迁移的应用
    
    这个精简版应用只初始化与数据库迁移相关的扩展，
    适用于'flask db'命令的执行环境。
    避免加载全部扩展以提高迁移命令的执行效率。
    
    :return: 数据库迁移专用的应用实例
    """
    app = create_flask_app_with_configs()
    from extensions import ext_database, ext_migrate

    # 仅初始化数据库和迁移相关扩展
    ext_database.init_app(app)
    ext_migrate.init_app(app)

    return app
