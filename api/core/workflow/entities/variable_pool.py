import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any, Union

from pydantic import BaseModel, Field

from core.file import File, FileAttribute, file_manager
from core.variables import Segment, SegmentGroup, Variable
from core.variables.segments import FileSegment, NoneSegment
from factories import variable_factory

from ..constants import CONVERSATION_VARIABLE_NODE_ID, ENVIRONMENT_VARIABLE_NODE_ID, SYSTEM_VARIABLE_NODE_ID
from ..enums import SystemVariableKey

# 变量值类型定义，支持字符串、整数、浮点数、字典、列表和文件
VariableValue = Union[str, int, float, dict, list, File]

# 变量模式正则表达式，用于匹配模板中的变量
VARIABLE_PATTERN = re.compile(r"\{\{#([a-zA-Z0-9_]{1,50}(?:\.[a-zA-Z_][a-zA-Z0-9_]{0,29}){1,10})#\}\}")


class VariablePool(BaseModel):
    """
    变量池实体类
    
    用于管理工作流中的变量，包括系统变量、环境变量、会话变量等。
    变量通过选择器（selector）进行访问，选择器的第一个元素是节点ID。
    
    属性：
    - variable_dictionary: 变量字典，用于通过选择器查找变量
    - user_inputs: 用户输入
    - system_variables: 系统变量
    - environment_variables: 环境变量
    - conversation_variables: 会话变量
    """

    # 变量字典是一个用于通过选择器查找变量的字典。
    # 选择器的第一个元素是节点ID，它是字典中的第一级键。
    # 选择器的其他元素是第二级字典中的键。为了获取键，我们对选择器中除第一个元素外的其他元素进行哈希。
    variable_dictionary: dict[str, dict[int, Segment]] = Field(
        description="变量映射",
        default=defaultdict(dict),
    )
    # TODO: 这个用户输入不用于池
    user_inputs: Mapping[str, Any] = Field(
        description="用户输入",
    )
    system_variables: Mapping[SystemVariableKey, Any] = Field(
        description="系统变量",
    )
    environment_variables: Sequence[Variable] = Field(
        description="环境变量",
        default_factory=list,
    )
    conversation_variables: Sequence[Variable] = Field(
        description="会话变量",
        default_factory=list,
    )

    def __init__(
        self,
        *,
        system_variables: Mapping[SystemVariableKey, Any] | None = None,
        user_inputs: Mapping[str, Any] | None = None,
        environment_variables: Sequence[Variable] | None = None,
        conversation_variables: Sequence[Variable] | None = None,
        **kwargs,
    ):
        """
        初始化变量池
        
        :param system_variables: 系统变量
        :param user_inputs: 用户输入
        :param environment_variables: 环境变量
        :param conversation_variables: 会话变量
        :param kwargs: 其他参数
        """
        environment_variables = environment_variables or []
        conversation_variables = conversation_variables or []
        user_inputs = user_inputs or {}
        system_variables = system_variables or {}

        super().__init__(
            system_variables=system_variables,
            user_inputs=user_inputs,
            environment_variables=environment_variables,
            conversation_variables=conversation_variables,
            **kwargs,
        )

        # 将系统变量添加到变量池
        for key, value in self.system_variables.items():
            self.add((SYSTEM_VARIABLE_NODE_ID, key.value), value)
        # 将环境变量添加到变量池
        for var in self.environment_variables:
            self.add((ENVIRONMENT_VARIABLE_NODE_ID, var.name), var)
        # 将会话变量添加到变量池
        for var in self.conversation_variables:
            self.add((CONVERSATION_VARIABLE_NODE_ID, var.name), var)

    def add(self, selector: Sequence[str], value: Any, /) -> None:
        """
        向变量池添加变量
        
        注意：即使现在允许，也不应该向变量池添加非Segment类型的值。
        
        :param selector: 变量的选择器
        :param value: 变量的值
        :raises ValueError: 如果选择器无效
        """
        if len(selector) < 2:
            raise ValueError("无效的选择器")

        if isinstance(value, Variable):
            variable = value
        if isinstance(value, Segment):
            variable = variable_factory.segment_to_variable(segment=value, selector=selector)
        else:
            segment = variable_factory.build_segment(value)
            variable = variable_factory.segment_to_variable(segment=segment, selector=selector)

        hash_key = hash(tuple(selector[1:]))
        self.variable_dictionary[selector[0]][hash_key] = variable

    def get(self, selector: Sequence[str], /) -> Segment | None:
        """
        根据选择器从变量池中获取值
        
        :param selector: 用于标识变量的选择器
        :return: 与给定选择器关联的值
        :raises ValueError: 如果选择器无效
        """
        if len(selector) < 2:
            return None

        hash_key = hash(tuple(selector[1:]))
        value = self.variable_dictionary[selector[0]].get(hash_key)

        if value is None:
            selector, attr = selector[:-1], selector[-1]
            # Python 3.12后支持 `attr in FileAttribute`
            if attr not in {item.value for item in FileAttribute}:
                return None
            value = self.get(selector)
            if not isinstance(value, FileSegment | NoneSegment):
                return None
            if isinstance(value, FileSegment):
                attr = FileAttribute(attr)
                attr_value = file_manager.get_attr(file=value.value, attr=attr)
                return variable_factory.build_segment(attr_value)
            return value

        return value

    def remove(self, selector: Sequence[str], /):
        """
        根据给定的选择器从变量池中移除变量
        
        :param selector: 表示选择器的字符串序列
        """
        if not selector:
            return
        if len(selector) == 1:
            self.variable_dictionary[selector[0]] = {}
            return
        hash_key = hash(tuple(selector[1:]))
        self.variable_dictionary[selector[0]].pop(hash_key, None)

    def convert_template(self, template: str, /):
        """
        将模板转换为段组
        
        :param template: 包含变量的模板字符串
        :return: 转换后的段组
        """
        parts = VARIABLE_PATTERN.split(template)
        segments = []
        for part in filter(lambda x: x, parts):
            if "." in part and (variable := self.get(part.split("."))):
                segments.append(variable)
            else:
                segments.append(variable_factory.build_segment(part))
        return SegmentGroup(value=segments)

    def get_file(self, selector: Sequence[str], /) -> FileSegment | None:
        """
        获取文件段
        
        :param selector: 文件的选择器
        :return: 文件段，如果不存在则返回None
        """
        segment = self.get(selector)
        if isinstance(segment, FileSegment):
            return segment
        return None
