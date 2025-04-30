"""
服务层错误处理模块

此模块集中管理所有服务层相关的错误定义。
每个子模块对应不同的业务领域，包含该领域特定的错误类型。

导出的错误模块包括：
- account: 账户相关的错误
- app: 应用相关的错误
- app_model_config: 应用模型配置相关的错误
- audio: 音频处理相关的错误
- base: 错误处理的基础类
- completion: 补全服务相关的错误
- conversation: 对话相关的错误
- dataset: 数据集相关的错误
- document: 文档处理相关的错误
- file: 文件处理相关的错误
- index: 索引相关的错误
- message: 消息处理相关的错误
"""

from . import (
    account,
    app,
    app_model_config,
    audio,
    base,
    completion,
    conversation,
    dataset,
    document,
    file,
    index,
    message,
)

__all__ = [
    "account",
    "app",
    "app_model_config",
    "audio",
    "base",
    "completion",
    "conversation",
    "dataset",
    "document",
    "file",
    "index",
    "message",
]
