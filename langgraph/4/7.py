from typing import TypedDict
from IPython.display import Image, display

from langgraph.constants import END, START
from langgraph.graph import StateGraph

class InputState(TypedDict):
    user_input: str

class OutputState(TypedDict):
    graph_output: str

class OverallState(TypedDict):
    foo: str
    user_input: InputState
    output_state: OutputState

class PrivateState(TypedDict):
    bar: str

def node_1(state: InputState) -> OutputState:
    '''
    写入OverallState的foo字段
    '''
    return {"foo":state["user_input"] + " >学院"}

def node_2(state: OverallState) -> PrivateState:
    '''
    读取OverallState, 写入PrivateState的bar字段
    '''
    return {"bar":state["foo"] + " >非常"}


def node_3(state: PrivateState) -> OutputState:
    '''
    读取PrivateState, 写入OverallState的output_state字段
    '''
    return {"graph_output":state["bar"] + " >棒"}


# 构建状态图
graph = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)
# 添加节点
graph.add_node("node_1", node_1)
graph.add_node("node_2", node_2)
graph.add_node("node_3", node_3)
# 添加边
graph.add_edge(START, "node_1")
graph.add_edge("node_1", "node_2")
graph.add_edge("node_2", "node_3")
graph.add_edge("node_3", END)
# 编译图
graph_1=graph.compile()
# 执行图
result = graph_1.invoke({"user_input":"清华"})
print(result)
display(Image(graph_1.get_graph().draw_mermaid_png()))