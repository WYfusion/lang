"""
演示 set_entry_point() 和 set_finish_point() 的区别
"""
from typing import TypedDict
from langgraph.graph import StateGraph
from langgraph.constants import END

class State(TypedDict):
    value: str

def node_a(state: State):
    print("执行 node_a")
    return {"value": state["value"] + " -> A"}

def node_b(state: State):
    print("执行 node_b")
    return {"value": state["value"] + " -> B"}

def node_c(state: State):
    print("执行 node_c")
    return {"value": state["value"] + " -> C"}

def node_d(state: State):
    print("执行 node_d")
    return {"value": state["value"] + " -> D"}

# ===== 示例 1: 设定 entry_point 和 finish_point =====
print("="*60)
print("示例 1: 设定入口和终止节点")
print("="*60)

graph1 = (StateGraph(State)
    .add_node("A", node_a)
    .add_node("B", node_b)
    .add_node("C", node_c)
    .add_node("D", node_d)
    
    # 添加边：连接各节点
    .add_edge("A", "B")
    .add_edge("B", "C")
    .add_edge("C", "D")
    
    # 设定入口节点：从 A 开始执行
    .set_entry_point("A")
    
    # 设定终止节点：执行到 C 时停止（不执行 D）
    .set_finish_point("C")
    
    .compile())

result1 = graph1.invoke({"value": "Start"})
print(f"结果: {result1['value']}")
print()

# ===== 示例 2: 没有设定 finish_point（执行到 END）=====
print("="*60)
print("示例 2: 没有设定终止节点（执行到 END）")
print("="*60)

graph2 = (StateGraph(State)
    .add_node("A", node_a)
    .add_node("B", node_b)
    .add_node("C", node_c)
    .add_node("D", node_d)
    
    # 添加边：连接各节点
    .add_edge("A", "B")
    .add_edge("B", "C")
    .add_edge("C", "D")
    .add_edge("D", END)  # 连接到 END 节点
    
    # 设定入口节点
    .set_entry_point("A")
    
    # 没有设定 finish_point，所以会执行到 END
    
    .compile())

result2 = graph2.invoke({"value": "Start"})
print(f"结果: {result2['value']}")
print()

# ===== 示例 3: 不同的入口点 =====
print("="*60)
print("示例 3: 从不同的节点作为入口")
print("="*60)

graph3 = (StateGraph(State)
    .add_node("A", node_a)
    .add_node("B", node_b)
    .add_node("C", node_c)
    .add_node("D", node_d)
    
    # 添加边
    .add_edge("A", "B")
    .add_edge("B", "C")
    .add_edge("C", "D")
    .add_edge("D", END)
    
    # 从 B 开始执行（跳过 A）
    .set_entry_point("B")
    
    .compile())

result3 = graph3.invoke({"value": "Start"})
print(f"结果: {result3['value']}")
print()

# ===== 总结 =====
print("="*60)
print("📌 总结")
print("="*60)
print("""
1. set_entry_point("X")
   - 设定图的入口节点为 X
   - 图执行从 X 开始

2. set_finish_point("X")
   - 设定图的终止节点为 X
   - 图执行到 X 时停止
   - 如果不设定，则执行到 END 节点

3. add_edge("X", "Y")
   - 设定从节点 X 到节点 Y 的边（连接）
   - 多条边组成完整的执行路径

4. 执行流程：
   START -> entry_point -> ... -> finish_point -> END
""")
