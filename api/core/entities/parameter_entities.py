from enum import StrEnum


class CommonParameterType(StrEnum):
    """
    通用参数类型枚举类
    
    定义系统中常用的参数类型，用于配置和参数验证。
    
    类型包括：
    - SECRET_INPUT: 密钥输入，用于敏感信息
    - TEXT_INPUT: 文本输入，用于普通文本
    - SELECT: 选择器，用于从预定义选项中选择
    - STRING: 字符串类型
    - NUMBER: 数字类型
    - FILE: 单个文件上传
    - FILES: 多个文件上传
    - SYSTEM_FILES: 系统文件选择
    - BOOLEAN: 布尔值
    - APP_SELECTOR: 应用选择器
    - MODEL_SELECTOR: 模型选择器
    - TOOLS_SELECTOR: 工具选择器（数组类型）
    """

    SECRET_INPUT = "secret-input"
    TEXT_INPUT = "text-input"
    SELECT = "select"
    STRING = "string"
    NUMBER = "number"
    FILE = "file"
    FILES = "files"
    SYSTEM_FILES = "system-files"
    BOOLEAN = "boolean"
    APP_SELECTOR = "app-selector"
    MODEL_SELECTOR = "model-selector"
    TOOLS_SELECTOR = "array[tools]"

    # TOOL_SELECTOR = "tool-selector"


class AppSelectorScope(StrEnum):
    """
    应用选择器作用域枚举类
    
    定义应用选择器的作用范围，用于限制应用的选择范围。
    
    作用域包括：
    - ALL: 所有应用
    - CHAT: 聊天应用
    - WORKFLOW: 工作流应用
    - COMPLETION: 补全应用
    """

    ALL = "all"
    CHAT = "chat"
    WORKFLOW = "workflow"
    COMPLETION = "completion"


class ModelSelectorScope(StrEnum):
    """
    模型选择器作用域枚举类
    
    定义模型选择器的作用范围，用于限制模型的选择范围。
    
    作用域包括：
    - LLM: 大语言模型
    - TEXT_EMBEDDING: 文本嵌入模型
    - RERANK: 重排序模型
    - TTS: 文本转语音模型
    - SPEECH2TEXT: 语音转文本模型
    - MODERATION: 内容审核模型
    - VISION: 视觉模型
    """

    LLM = "llm"
    TEXT_EMBEDDING = "text-embedding"
    RERANK = "rerank"
    TTS = "tts"
    SPEECH2TEXT = "speech2text"
    MODERATION = "moderation"
    VISION = "vision"


class ToolSelectorScope(StrEnum):
    """
    工具选择器作用域枚举类
    
    定义工具选择器的作用范围，用于限制工具的选择范围。
    
    作用域包括：
    - ALL: 所有工具
    - CUSTOM: 自定义工具
    - BUILTIN: 内置工具
    - WORKFLOW: 工作流工具
    """

    ALL = "all"
    CUSTOM = "custom"
    BUILTIN = "builtin"
    WORKFLOW = "workflow"
