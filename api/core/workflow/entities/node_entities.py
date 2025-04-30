from collections.abc import Mapping
from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel

from core.model_runtime.entities.llm_entities import LLMUsage
from models.workflow import WorkflowNodeExecutionStatus


class NodeRunMetadataKey(StrEnum):
    """
    节点运行元数据键枚举类
    
    定义节点运行过程中可能产生的各种元数据键。
    
    键包括：
    - TOTAL_TOKENS: 总token数
    - TOTAL_PRICE: 总价格
    - CURRENCY: 货币单位
    - TOOL_INFO: 工具信息
    - AGENT_LOG: 代理日志
    - ITERATION_ID: 迭代ID
    - ITERATION_INDEX: 迭代索引
    - LOOP_ID: 循环ID
    - LOOP_INDEX: 循环索引
    - PARALLEL_ID: 并行ID
    - PARALLEL_START_NODE_ID: 并行起始节点ID
    - PARENT_PARALLEL_ID: 父并行ID
    - PARENT_PARALLEL_START_NODE_ID: 父并行起始节点ID
    - PARALLEL_MODE_RUN_ID: 并行模式运行ID
    - ITERATION_DURATION_MAP: 迭代持续时间映射
    - LOOP_DURATION_MAP: 循环持续时间映射
    - ERROR_STRATEGY: 错误处理策略
    - LOOP_VARIABLE_MAP: 循环变量映射
    """

    TOTAL_TOKENS = "total_tokens"
    TOTAL_PRICE = "total_price"
    CURRENCY = "currency"
    TOOL_INFO = "tool_info"
    AGENT_LOG = "agent_log"
    ITERATION_ID = "iteration_id"
    ITERATION_INDEX = "iteration_index"
    LOOP_ID = "loop_id"
    LOOP_INDEX = "loop_index"
    PARALLEL_ID = "parallel_id"
    PARALLEL_START_NODE_ID = "parallel_start_node_id"
    PARENT_PARALLEL_ID = "parent_parallel_id"
    PARENT_PARALLEL_START_NODE_ID = "parent_parallel_start_node_id"
    PARALLEL_MODE_RUN_ID = "parallel_mode_run_id"
    ITERATION_DURATION_MAP = "iteration_duration_map"  # single iteration duration if iteration node runs
    LOOP_DURATION_MAP = "loop_duration_map"  # single loop duration if loop node runs
    ERROR_STRATEGY = "error_strategy"  # node in continue on error mode return the field
    LOOP_VARIABLE_MAP = "loop_variable_map"  # single loop variable output


class NodeRunResult(BaseModel):
    """
    节点运行结果实体类
    
    用于存储节点运行的结果信息，包括状态、输入输出、元数据等。
    
    属性：
    - status: 节点执行状态
    - inputs: 节点输入数据
    - process_data: 处理过程中的数据
    - outputs: 节点输出数据
    - metadata: 节点元数据
    - llm_usage: LLM使用情况
    - edge_source_handle: 多分支节点的源句柄ID
    - error: 错误信息（如果状态为失败）
    - error_type: 错误类型（如果状态为失败）
    - retry_index: 重试次数
    """

    status: WorkflowNodeExecutionStatus = WorkflowNodeExecutionStatus.RUNNING

    inputs: Optional[Mapping[str, Any]] = None  # node inputs
    process_data: Optional[Mapping[str, Any]] = None  # process data
    outputs: Optional[Mapping[str, Any]] = None  # node outputs
    metadata: Optional[Mapping[NodeRunMetadataKey, Any]] = None  # node metadata
    llm_usage: Optional[LLMUsage] = None  # llm usage

    edge_source_handle: Optional[str] = None  # source handle id of node with multiple branches

    error: Optional[str] = None  # error message if status is failed
    error_type: Optional[str] = None  # error type if status is failed

    # single step node run retry
    retry_index: int = 0


class AgentNodeStrategyInit(BaseModel):
    """
    代理节点策略初始化实体类
    
    用于初始化代理节点的策略配置。
    
    属性：
    - name: 策略名称
    - icon: 策略图标（可选）
    """

    name: str
    icon: str | None = None
