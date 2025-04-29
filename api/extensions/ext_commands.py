from dify_app import DifyApp


def init_app(app: DifyApp):
    """
    初始化命令行接口扩展
    
    注册各种Flask CLI命令，用于系统管理、维护和调试。
    这些命令可以通过'flask 命令名'的方式在终端中执行，
    提供了对系统进行各种管理操作的便捷方式。
    
    :param app: Flask应用实例
    """
    from commands import (
        add_qdrant_index,                    # 添加Qdrant向量索引
        clear_free_plan_tenant_expired_logs, # 清理免费计划租户过期日志
        convert_to_agent_apps,               # 将应用转换为Agent应用
        create_tenant,                       # 创建租户
        extract_plugins,                     # 提取插件
        extract_unique_plugins,              # 提取唯一插件
        fix_app_site_missing,                # 修复应用站点缺失问题
        install_plugins,                     # 安装插件
        migrate_data_for_plugin,             # 为插件迁移数据
        old_metadata_migration,              # 旧元数据迁移
        reset_email,                         # 重置电子邮件
        reset_encrypt_key_pair,              # 重置加密密钥对
        reset_password,                      # 重置密码
        upgrade_db,                          # 升级数据库
        vdb_migrate,                         # 向量数据库迁移
    )

    # 需要注册的命令列表
    cmds_to_register = [
        reset_password,
        reset_email,
        reset_encrypt_key_pair,
        vdb_migrate,
        convert_to_agent_apps,
        add_qdrant_index,
        create_tenant,
        upgrade_db,
        fix_app_site_missing,
        migrate_data_for_plugin,
        extract_plugins,
        extract_unique_plugins,
        install_plugins,
        old_metadata_migration,
        clear_free_plan_tenant_expired_logs,
    ]
    
    # 将每个命令添加到Flask CLI
    for cmd in cmds_to_register:
        app.cli.add_command(cmd)
