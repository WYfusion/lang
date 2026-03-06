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
    # user_input: InputState
    # output_state: OutputState

class PrivateState(TypedDict):
    bar: str

def node_1(state: InputState) -> OverallState:
    '''
    state 参数是必需的，因为节点函数需要接受一个状态对象作为输入。
    这个状态对象包含了当前图的状态信息，节点函数通过读取这个状态对象来获取输入数据，并通过返回一个新的状态对象来输出结果。
    写入OverallState的foo字段，注意需要和OverallState定义的字段一致
    '''
    return {"foo":state["user_input"] + " >学院"}

def node_2(state: OverallState) -> PrivateState:
    '''
    读取OverallState, 写入PrivateState的bar字段，注意需要和PrivateState定义的字段一致
    '''
    return {"bar":state["foo"] + " >非常"}


def node_3(state: PrivateState) -> OutputState:
    '''
    读取PrivateState, 写入OverallState的output_state字段，注意需要和OutputState定义的字段一致
    '''
    return {"graph_output":state["bar"] + " >棒"}


# 构建状态图
graph = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)
# 添加节点
graph.add_node("node_1", node_1)
graph.add_node("node_2", node_2)
graph.add_node("node_3", node_3)
# 添加边
# 这里的节点的链接关系是：START -> node_1 -> node_2 -> node_3 -> END。
graph.add_edge(START, "node_1") # 从 START 开始执行，进入 node_1
graph.add_edge("node_1", "node_2") # node_1 执行完后进入 node_2，注意这里的node_1输出状态必须匹配node_2的输入状态(不用完全匹配，只要包含 node_2 输入状态定义的字段即可)
graph.add_edge("node_2", "node_3")
graph.add_edge("node_3", END)
# 编译图
graph_1=graph.compile()
# 执行图
result = graph_1.invoke({"user_input":"清华"})
print(result)
# display(Image(graph_1.get_graph().draw_mermaid_png()))
img = graph_1.get_graph().draw_mermaid_png()

# 兼容不同版本返回值：有的版本返回 bytes，有的返回带 data 属性的对象
png_bytes = img if isinstance(img, bytes) else img.data
with open("graph.png", "wb") as f:
    f.write(png_bytes)

print("已生成图片: graph.png")