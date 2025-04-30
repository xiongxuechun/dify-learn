from typing import Optional

from pydantic import BaseModel

from core.app.entities.app_invoke_entities import InvokeFrom
from core.workflow.nodes.base import BaseIterationState, BaseLoopState, BaseNode
from models.enums import UserFrom
from models.workflow import Workflow, WorkflowType

from .node_entities import NodeRunResult
from .variable_pool import VariablePool


class WorkflowNodeAndResult:
    """
    工作流节点和结果实体类
    
    用于存储工作流节点及其运行结果。
    
    属性：
    - node: 工作流节点实例
    - result: 节点运行结果（可选）
    """

    node: BaseNode
    result: Optional[NodeRunResult] = None

    def __init__(self, node: BaseNode, result: Optional[NodeRunResult] = None):
        """
        初始化工作流节点和结果
        
        :param node: 工作流节点实例
        :param result: 节点运行结果（可选）
        """
        self.node = node
        self.result = result


class WorkflowRunState:
    """
    工作流运行状态实体类
    
    用于跟踪和管理工作流的运行状态，包括节点执行、变量池、迭代状态等。
    
    属性：
    - tenant_id: 租户ID
    - app_id: 应用ID
    - workflow_id: 工作流ID
    - workflow_type: 工作流类型
    - user_id: 用户ID
    - user_from: 用户来源
    - invoke_from: 调用来源
    - workflow_call_depth: 工作流调用深度
    - start_at: 开始时间
    - variable_pool: 变量池
    - total_tokens: 总token数
    - workflow_nodes_and_results: 工作流节点和结果列表
    - workflow_node_runs: 工作流节点运行记录
    - workflow_node_steps: 工作流节点步骤数
    - current_iteration_state: 当前迭代状态
    - current_loop_state: 当前循环状态
    """

    tenant_id: str
    app_id: str
    workflow_id: str
    workflow_type: WorkflowType
    user_id: str
    user_from: UserFrom
    invoke_from: InvokeFrom

    workflow_call_depth: int

    start_at: float
    variable_pool: VariablePool

    total_tokens: int = 0

    workflow_nodes_and_results: list[WorkflowNodeAndResult]

    class NodeRun(BaseModel):
        """
        节点运行记录实体类
        
        用于记录节点的运行信息。
        
        属性：
        - node_id: 节点ID
        - iteration_node_id: 迭代节点ID
        - loop_node_id: 循环节点ID
        """

        node_id: str
        iteration_node_id: str
        loop_node_id: str

    workflow_node_runs: list[NodeRun]
    workflow_node_steps: int

    current_iteration_state: Optional[BaseIterationState]
    current_loop_state: Optional[BaseLoopState]

    def __init__(
        self,
        workflow: Workflow,
        start_at: float,
        variable_pool: VariablePool,
        user_id: str,
        user_from: UserFrom,
        invoke_from: InvokeFrom,
        workflow_call_depth: int,
    ):
        """
        初始化工作流运行状态
        
        :param workflow: 工作流实例
        :param start_at: 开始时间
        :param variable_pool: 变量池
        :param user_id: 用户ID
        :param user_from: 用户来源
        :param invoke_from: 调用来源
        :param workflow_call_depth: 工作流调用深度
        """
        self.workflow_id = workflow.id
        self.tenant_id = workflow.tenant_id
        self.app_id = workflow.app_id
        self.workflow_type = WorkflowType.value_of(workflow.type)
        self.user_id = user_id
        self.user_from = user_from
        self.invoke_from = invoke_from
        self.workflow_call_depth = workflow_call_depth

        self.start_at = start_at
        self.variable_pool = variable_pool

        self.total_tokens = 0

        self.workflow_node_steps = 1
        self.workflow_node_runs = []
        self.current_iteration_state = None
        self.current_loop_state = None
