"""
LangGraph Send 动态路由教程
版本: LangGraph 1.0.10

本教程演示如何使用 Send 实现从一个节点动态路由到多个节点的功能。
Send 允许在运行时决定路由到哪些节点，是实现动态并行处理的关键。
"""

from typing import List, Dict, Any, TypedDict, Union, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from operator import add


# ==================== 1. 定义状态 ====================

class OverallState(TypedDict):
    """整体图状态"""
    items: List[str]  # 需要处理的物品列表
    results: Annotated[List[Dict[str, Any]], add]  # 处理结果 - 使用 Annotated 支持并发写入
    condition: str  # 条件判断


class ItemState(TypedDict):
    """单个物品处理状态"""
    item: str  # 当前处理的物品
    step: str  # 当前步骤


# ==================== 2. 定义处理节点 ====================

def start_node(state: OverallState) -> Dict[str, Any]:
    """
    起始节点：准备数据并决定路由
    """
    print(f"\n{'='*50}")
    print("【起始节点】开始处理")
    print(f"待处理物品: {state['items']}")
    print(f"条件: {state['condition']}")
    
    # 动态决定要路由到哪些节点
    # 这里我们会返回一个 Send 对象列表，每个 Send 指定目标节点和状态
    sends = []
    for item in state['items']:
        sends.append(Send("process_item", {"item": item, "step": "initial"}))
    
    # 根据条件决定是否发送额外处理
    if state['condition'] == 'special':
        sends.append(Send("special_process", {"item": "SPECIAL_ITEM", "step": "special"}))
    
    print(f"准备路由到 {len(sends)} 个节点")
    print(f"{'='*50}\n")
    
    return {"results": []}  # 初始化结果列表


def process_item_node(state: ItemState) -> Dict[str, Any]:
    """
    普通处理节点：处理单个物品
    """
    print(f"【处理节点】处理物品: {state['item']}")
    
    # 模拟处理逻辑
    processed_result = {
        "item": state['item'],
        "status": "processed",
        "value": len(state['item']) * 10,  # 简单处理：字符串长度乘以10
        "node_type": "normal"
    }
    
    return {"results": [processed_result]}


def special_process_node(state: ItemState) -> Dict[str, Any]:
    """
    特殊处理节点：处理特殊物品
    """
    print(f"【特殊处理节点】处理特殊物品: {state['item']}")
    
    # 特殊处理逻辑
    special_result = {
        "item": state['item'],
        "status": "special_processed",
        "value": 999,
        "node_type": "special",
        "priority": "high"
    }
    
    return {"results": [special_result]}


def collect_results_node(state: OverallState) -> Dict[str, Any]:
    """
    收集结果节点：汇总所有处理结果
    """
    print(f"\n{'='*50}")
    print("【收集节点】汇总所有结果")
    print(f"收集到 {len(state['results'])} 个结果:")
    
    for result in state['results']:
        print(f"  - {result}")
    
    # 计算总和
    total_value = sum(result.get('value', 0) for result in state['results'])
    print(f"总价值: {total_value}")
    print(f"{'='*50}\n")
    
    return {
        "summary": {
            "total_items": len(state['results']),
            "total_value": total_value,
            "results": state['results']
        }
    }


# ==================== 3. 构建动态路由图 ====================

def create_dynamic_send_graph() -> StateGraph:
    """
    创建使用 Send 动态路由的图
    """
    # 创建状态图
    workflow = StateGraph(OverallState)
    
    # 添加节点
    workflow.add_node("start", start_node)
    workflow.add_node("process_item", process_item_node)
    workflow.add_node("special_process", special_process_node)
    workflow.add_node("collect", collect_results_node)
    
    # 设置入口点
    workflow.set_entry_point("start")
    
    # 添加动态路由边
    # 关键点：start 节点的输出会被用来创建 Send 对象，动态路由到多个节点
    workflow.add_conditional_edges(
        "start",
        # 这个函数返回 Send 对象列表，每个 Send 指定目标节点和输入状态
        lambda state: [
            Send("process_item", {"item": item, "step": "initial"})
            for item in state["items"]
        ] + ([Send("special_process", {"item": "SPECIAL_ITEM", "step": "special"})]
             if state["condition"] == "special" else []),
        # 路径映射 - 告诉 LangGraph 可能的目标节点
        ["process_item", "special_process"]
    )
    
    # 从处理节点到收集节点
    # 注意：所有 process_item 和 special_process 节点都会汇聚到 collect
    workflow.add_edge("process_item", "collect")
    workflow.add_edge("special_process", "collect")
    
    # 设置结束点
    workflow.set_finish_point("collect")
    
    return workflow

img = create_dynamic_send_graph().compile().get_graph().draw_mermaid_png()
# 兼容不同版本返回值：有的版本返回 bytes，有的返回带 data 属性的对象
png_bytes = img if isinstance(img, bytes) else img.data
with open("graph15.png", "wb") as f:
    f.write(png_bytes)

print("已生成图片: graph15.png")

print("已生成图片: graph15.png")
# ==================== 4. 使用示例 ====================

def run_example_1():
    """
    示例 1: 基本动态路由
    """
    print("\n" + "="*60)
    print("示例 1: 基本动态路由 - 处理多个物品")
    print("="*60)
    
    # 创建图
    workflow = create_dynamic_send_graph()
    app = workflow.compile()
    
    # 初始状态
    initial_state = {
        "items": ["apple", "banana", "cherry"],
        "results": [],
        "condition": "normal"
    }
    
    # 运行图
    result = app.invoke(initial_state)
    
    print("\n最终状态:")
    print(result)


def run_example_2():
    """
    示例 2: 带特殊条件的动态路由
    """
    print("\n" + "="*60)
    print("示例 2: 带特殊条件的动态路由 - 触发特殊处理")
    print("="*60)
    
    # 创建图
    workflow = create_dynamic_send_graph()
    app = workflow.compile()
    
    # 初始状态 - 设置特殊条件
    initial_state = {
        "items": ["item1", "item2"],
        "results": [],
        "condition": "special"  # 特殊条件会触发额外处理
    }
    
    # 运行图
    result = app.invoke(initial_state)
    
    print("\n最终状态:")
    print(result)


def run_example_3():
    """
    示例 3: 空列表测试
    """
    print("\n" + "="*60)
    print("示例 3: 空列表 - 没有动态路由")
    print("="*60)
    
    # 创建图
    workflow = create_dynamic_send_graph()
    app = workflow.compile()
    
    # 初始状态 - 空列表
    initial_state = {
        "items": [],
        "results": [],
        "condition": "normal"
    }
    
    # 运行图
    result = app.invoke(initial_state)
    
    print("\n最终状态:")
    print(result)


# ==================== 5. 高级示例：嵌套动态路由 ====================

class NestedState(TypedDict):
    data: List[Dict[str, Any]]
    level: int
    final_results: Annotated[List[str], add]


def entry_node(state: NestedState) -> NestedState:
    """
    入口节点：打印信息并传递状态
    """
    print(f"\n{'='*50}")
    print(f"【入口节点】处理 {len(state['data'])} 个任务，层级: {state['level']}")
    print(f"{'='*50}\n")
    return state


def advanced_router(state: NestedState) -> List[Send]:
    """
    高级路由函数：根据数据类型动态路由到不同节点
    """
    sends = []
    
    for item in state["data"]:
        if item["type"] == "simple":
            sends.append(Send("simple_process", {"item": item, "level": state["level"]}))
        elif item["type"] == "complex":
            sends.append(Send("complex_process", {"item": item, "level": state["level"]}))
        elif item["type"] == "recursive" and state["level"] < 2:
            # 递归处理：创建新的子任务
            sends.append(Send("recursive_process", {"item": item, "level": state["level"] + 1}))
    
    return sends


def simple_process(state: Dict) -> Dict:
    print(f"【简单处理】层级 {state['level']}: {state['item']['name']}")
    return {"final_results": [f"Simple: {state['item']['name']}"]}


def complex_process(state: Dict) -> Dict:
    print(f"【复杂处理】层级 {state['level']}: {state['item']['name']}")
    return {"final_results": [f"Complex: {state['item']['name']}"]}


def recursive_process(state: Dict) -> Dict:
    print(f"【递归处理】层级 {state['level']}: {state['item']['name']}")
    # 递归创建更多任务
    return {"final_results": [f"Recursive: {state['item']['name']} at level {state['level']}"]}


def create_advanced_graph() -> StateGraph:
    """
    创建高级动态路由图
    """
    workflow = StateGraph(NestedState)
    
    workflow.add_node("entry", entry_node)
    workflow.add_node("simple_process", simple_process)
    workflow.add_node("complex_process", complex_process)
    workflow.add_node("recursive_process", recursive_process)
    workflow.add_node("aggregator", lambda state: {"final_results": state.get("final_results", [])})
    
    workflow.set_entry_point("entry")
    # 从 entry 节点使用 advanced_router 进行动态路由
    workflow.add_conditional_edges("entry", advanced_router, 
                                   ["simple_process", "complex_process", "recursive_process"])
    workflow.add_edge("simple_process", "aggregator")
    workflow.add_edge("complex_process", "aggregator")
    workflow.add_edge("recursive_process", "aggregator")
    workflow.set_finish_point("aggregator")
    
    return workflow


def run_example_4():
    """
    示例 4: 高级动态路由 - 不同类型不同处理
    """
    print("\n" + "="*60)
    print("示例 4: 高级动态路由 - 根据类型选择处理")
    print("="*60)
    
    workflow = create_advanced_graph()
    app = workflow.compile()
    
    initial_state = {
        "data": [
            {"type": "simple", "name": "Task1"},
            {"type": "complex", "name": "Task2"},
            {"type": "recursive", "name": "Task3"},
            {"type": "simple", "name": "Task4"}
        ],
        "level": 0,
        "final_results": []
    }
    
    result = app.invoke(initial_state)
    print("\n最终结果:")
    for r in result["final_results"]:
        print(f"  - {r}")


# ==================== 6. 运行所有示例 ====================

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# LangGraph Send 动态路由教程")
    print("# 版本: LangGraph 1.0.10")
    print("#"*60)
    
    # 运行示例
    run_example_1()
    run_example_2()
    run_example_3()
    run_example_4()
    
    print("\n" + "#"*60)
    print("# 教程完成")
    print("#"*60 + "\n")
