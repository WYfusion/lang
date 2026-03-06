"""
演示 LangGraph 节点函数的参数用法
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, AIMessage
from langgraph.types import RunnableConfig

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    counter: int

# ===== 示例 1: 最简单的参数（只有 state）=====
def node_simple(state: State):
    """最常见的写法：只接收 state 参数"""
    print(f"✓ node_simple: state = {state}")
    return {"counter": state["counter"] + 1}

# ===== 示例 2: 接收 state 和 config 参数 =====
def node_with_config(state: State, config: RunnableConfig):
    """
    接收 state 和 config
    config 包含运行时配置信息（tags、callbacks 等）
    """
    print(f"✓ node_with_config: state counter = {state['counter']}")
    print(f"  config = {config}")
    new_message = AIMessage(f"Processing with config: {config}")
    return {"messages": [new_message], "counter": state["counter"] + 10}

# ===== 示例 3: 接收 state、config 和 **kwargs =====
def node_with_kwargs(state: State, config: RunnableConfig = None, **kwargs):
    """
    使用 **kwargs 来接收可能的其他参数
    这样更灵活，可以接收 LangGraph 可能传入的任何其他参数
    """
    print(f"✓ node_with_kwargs: state counter = {state['counter']}")
    print(f"  extra kwargs = {kwargs}")
    return {"counter": state["counter"] + 100}

# ===== 示例 4: 错误示例（不要这样做）=====
# def node_with_custom_param(state: State, my_custom_param: int):
#     """这会报错！LangGraph 不会注入自定义参数"""
#     return {"counter": state["counter"] + my_custom_param}

# ===== 构建图 =====
graph = (StateGraph(State)
    .add_node("node_simple", node_simple)
    .add_node("node_with_config", node_with_config)
    .add_node("node_with_kwargs", node_with_kwargs)
    .set_entry_point("node_simple")
    .add_edge("node_simple", "node_with_config")
    .add_edge("node_with_config", "node_with_kwargs")
    .compile())

# ===== 执行图 =====
result = graph.invoke({
    "messages": [],
    "counter": 0
})


img = graph.get_graph().draw_mermaid_png()

# 兼容不同版本返回值：有的版本返回 bytes，有的返回带 data 属性的对象
png_bytes = img if isinstance(img, bytes) else img.data
with open("graph.png", "wb") as f:
    f.write(png_bytes)

print("已生成图片: graph.png")
print("\n" + "="*50)
print("最终结果:")
print(f"Counter: {result['counter']}")
print("="*50)

# ===== 参考信息 =====
print("""
📌 总结：
1. ✓ state 参数：必需，接收当前图状态
2. ✓ config 参数：可选，接收运行时配置
3. ✓ **kwargs：可选，接收其他可能的参数
4. ✗ 自定义参数：不允许，LangGraph 只能注入认识的参数

如果需要向节点传递外部数据，应该：
- 将数据放在 state 中，通过状态传递
- 或使用 config 的 configurable 参数
""")
