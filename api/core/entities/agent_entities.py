from enum import Enum


class PlanningStrategy(Enum):
    """
    规划策略枚举类
    
    定义代理可以使用的不同规划策略，用于决定代理如何执行任务和做出决策。
    
    策略包括：
    - ROUTER: 路由策略，根据输入选择不同的处理路径
    - REACT_ROUTER: 反应式路由策略，结合反应式思考和路由选择
    - REACT: 反应式策略，基于观察-思考-行动的循环
    - FUNCTION_CALL: 函数调用策略，通过调用预定义函数来完成任务
    """

    ROUTER = "router"
    REACT_ROUTER = "react_router"
    REACT = "react"
    FUNCTION_CALL = "function_call"
