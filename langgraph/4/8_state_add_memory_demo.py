from langchain_core.messages import AnyMessage, AIMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from typing import Annotated,TypedDict
from operator import add

class State(TypedDict):
    '''
    Annotated 是 Python 的类型提示机制，允许在类型定义上附加元数据。
    在 LangGraph 中，它用于指定状态字段如何在多个节点之间合并更新。
    设计是因为在 AI 应用中，你通常想保留对话历史和状态演进，而不是每次都丢弃。
    langgraph.graph.message.MessagesState 类就是使用 Annotated 来定义一个消息列表字段，并指定使用 add_messages 函数来合并更新。
    '''
    messages: Annotated[list[AnyMessage], add_messages] # 定义一个消息列表字段，并指定使用 add_messages 函数来合并更新
    list_field: Annotated[list[int],add]    # 定义一个整数列表字段，并指定使用内置的 add 函数来合并更新
    extra_field: int    # 没有 Annotated（如 extra_field: int）：直接覆盖旧值

def node1(state: State):
    new_message = AIMessage("Hello!")
    return {"messages": [new_message],"list_field":[10],"extra_field": 10}

def node2(state: State):
    new_message = AIMessage("LangGraph!")
    return {"messages": [new_message], "list_field":[20],"extra_field": 20}


graph = (StateGraph(State)
        .add_node("node1",node1)
        .add_node("node2",node2)
        .set_entry_point("node1")
        .add_edge("node1", "node2")
        .compile())
input_message = {"role": "user", "content": "Hi"}
result = graph.invoke({"messages": [input_message], "list_field": [1,2,3]})
print(result)