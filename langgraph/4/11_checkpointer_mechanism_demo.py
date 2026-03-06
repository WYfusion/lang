"""
LangGraph 检查点机制演示 (Checkpointer)
检查点用于保存图的执行状态，支持断点续传和长期多轮交互
"""
from typing import TypedDict
from langgraph.graph import StateGraph
from langgraph.constants import END
from langgraph.checkpoint.memory import MemorySaver
import time
import json

class ConversationState(TypedDict):
    messages: list[str]
    user_input: str
    assistant_response: str
    turn: int

print("="*70)
print("LangGraph 检查点机制演示 - Checkpointer")
print("="*70)
print()

# ===== 演示 1: 检查点的基本概念 =====
print("【演示 1】检查点基本概念 - 为什么需要检查点？")
print("-" * 70)
print("""
检查点（Checkpointer）的作用：
1. 保存图执行状态：在每个节点执行完毕后保存当前状态
2. 支持断点续传：当图执行中断后，可以从上次的位置继续执行
3. 支持多轮交互：保存对话历史，支持长期的交互会话
4. 增强可靠性：即使发生错误，也不会丢失之前的工作

检查点 vs 缓存的区别：
- 检查点：保存整个图的执行状态（什么时候执行、执行了哪些步骤）
- 缓存：保存单个节点的执行结果（用来避免重复计算）
""")

print()

# ===== 演示 2: 使用 MemorySaver（内存检查点）=====
print("="*70)
print("【演示 2】MemorySaver - 内存检查点")
print("-" * 70)

def process_input(state: ConversationState):
    """处理用户输入"""
    print(f"  📥 接收输入: {state['user_input']}")
    
    # 模拟处理
    time.sleep(0.1)
    
    messages = state["messages"].copy()
    messages.append(f"User: {state['user_input']}")
    
    print(f"  ✓ 已保存到消息列表")
    
    return {
        "messages": messages,
        "turn": state["turn"] + 1
    }

def generate_response(state: ConversationState):
    """生成助手响应"""
    print(f"  🤖 生成响应...")
    
    # 模拟 LLM 调用
    time.sleep(0.1)
    
    response = f"这是对 '{state['user_input']}' 的回应"
    messages = state["messages"].copy()
    messages.append(f"Assistant: {response}")
    
    print(f"  ✓ 响应: {response}")
    
    return {
        "assistant_response": response,
        "messages": messages
    }

# 构建带检查点的图
checkpointer = MemorySaver()

graph = (StateGraph(ConversationState)
    .add_node("input_processor", process_input)
    .add_node("response_generator", generate_response)
    .set_entry_point("input_processor")
    .add_edge("input_processor", "response_generator")
    .add_edge("response_generator", END)
    .compile(checkpointer=checkpointer))

print("执行多轮对话（同一 session）:\n")

# 第一轮
print("第 1 轮:")
result1 = graph.invoke(
    {
        "messages": [],
        "user_input": "你好，今天天气如何？",
        "assistant_response": "",
        "turn": 0
    },
    config={"thread_id": "user_123"}
)
print(f"对话历史: {json.dumps(result1['messages'], ensure_ascii=False, indent=2)}\n")

# 第二轮
print("第 2 轮:")
result2 = graph.invoke(
    {
        "messages": result1["messages"],
        "user_input": "推荐一些好的编程语言",
        "assistant_response": "",
        "turn": result1["turn"]
    },
    config={"thread_id": "user_123"}
)
print(f"对话历史: {json.dumps(result2['messages'], ensure_ascii=False, indent=2)}\n")

# 第三轮
print("第 3 轮:")
result3 = graph.invoke(
    {
        "messages": result2["messages"],
        "user_input": "Python 有什么优势？",
        "assistant_response": "",
        "turn": result2["turn"]
    },
    config={"thread_id": "user_123"}
)
print(f"对话历史: {json.dumps(result3['messages'], ensure_ascii=False, indent=2)}\n")

print(f"✅ 总轮数: {result3['turn']}")
print("说明: 每一轮的状态都被保存在内存中，支持后续继续对话\n")
print()

# ===== 演示 3: 多个独立 session =====
print("="*70)
print("【演示 3】独立 Session - 不同用户的隔离")
print("-" * 70)

print("两个不同用户的对话隔离测试:\n")

# 用户 1
print("用户 1 (thread_id='user_001'):")
user1_result = graph.invoke(
    {
        "messages": [],
        "user_input": "我想学 Python",
        "assistant_response": "",
        "turn": 0
    },
    config={"thread_id": "user_001"}
)
print(f"消息数: {len(user1_result['messages'])}\n")

# 用户 2
print("用户 2 (thread_id='user_002'):")
user2_result = graph.invoke(
    {
        "messages": [],
        "user_input": "我想学 JavaScript",
        "assistant_response": "",
        "turn": 0
    },
    config={"thread_id": "user_002"}
)
print(f"消息数: {len(user2_result['messages'])}\n")

# 用户 1 继续对话
print("用户 1 继续对话:")
user1_continue = graph.invoke(
    {
        "messages": user1_result["messages"],
        "user_input": "怎样入门?",
        "assistant_response": "",
        "turn": user1_result["turn"]
    },
    config={"thread_id": "user_001"}
)
print(f"消息数: {len(user1_continue['messages'])}")
print(f"对话历史: {user1_continue['messages']}\n")

print("✅ 用户数据完全隔离，互不影响\n")
print()

# ===== 演示 4: 检查点存储在不同库中的概念 =====
print("="*70)
print("【演示 4】不同检查点存储方案介绍")
print("-" * 70)

print("""
LangGraph 支持多种检查点存储方案：

1️⃣  MemorySaver（内存检查点）
   ├─ 存储位置: 程序内存
   ├─ 持久化: ✗ 否（程序重启后丢失）
   ├─ 适用场景: 开发测试、短期应用
   └─ 优势: 配置简单、无需数据库
   
   >>> from langgraph.checkpoint.memory import MemorySaver
   >>> checkpointer = MemorySaver()

2️⃣  SqliteSaver（SQLite 检查点）
   ├─ 存储位置: SQLite 数据库文件
   ├─ 持久化: ✓ 是
   ├─ 适用场景: 单机生产部署
   └─ 优势: 轻量级、支持持久化
   
   >>> from langgraph.checkpoint.sqlite import SqliteSaver
   >>> checkpointer = SqliteSaver("./checkpoints.db")

3️⃣  PostgresSaver（PostgreSQL 检查点）
   ├─ 存储位置: PostgreSQL 数据库
   ├─ 持久化: ✓ 是
   ├─ 适用场景: 分布式生产部署
   └─ 优势: 高性能、支持多进程共享
   
   >>> from langgraph.checkpoint.postgres import PostgresSaver
   >>> checkpointer = PostgresSaver(connection_string)

本演示使用 MemorySaver，仅作为演示需要。
实际生产环境通常使用 SqliteSaver 或 PostgresSaver。
""")

print()

# ===== 演示 5: 检查点工作原理 =====
print("="*70)
print("【演示 5】检查点工作原理图解")
print("="*70)
print("""
检查点保存流程：

【第 1 轮呼叫】
  初始状态: {"messages": [], "user_input": "hello", "turn": 0}
       ↓
  执行 input_processor
       ↓
  生成中间状态: {..., "messages": ["User: hello"], ...}
       ↓
  📍 检查点保存 (thread_id, version=1)
       ↓
  执行 response_generator
       ↓
  生成最终状态: {..., "messages": ["User: hello", "Assistant: ..."], ...}
       ↓
  📍 检查点保存 (thread_id, version=2)

【第 2 轮呼叫】
  前一次保存的状态: {..., "messages": ["User: hello", "Assistant: ..."], ...}
       ↓
  继续执行下一步或新的输入
       ↓
  📍 检查点保存 (thread_id, version=3)

═══════════════════════════════════════════════════════════════════════

检查点对象的职责：

1. 保存（Save）
   - 在每个节点执行后保存当前的图状态
   - 记录 thread_id、version 等元数据

2. 读取（Get）
   - 根据 thread_id 和 version 读取之前保存的状态
   - 用于断点续传

3. 查询（List）
   - 列出某个 thread_id 的所有检查点版本
   - 用于查看对话历史

4. 删除（Delete）
   - 清理不需要的检查点数据
   - 释放存储空间
""")

print()

# ===== 演示 6: 不同检查点的对比 =====
print("="*70)
print("【演示 6】不同检查点存储方案对比")
print("="*70)
print("""
┌─────────────────────┬──────────────────┬──────────────┬──────────────┐
│ 检查点类型           │ 存储位置         │ 持久化        │ 适用场景      │
├─────────────────────┼──────────────────┼──────────────┼──────────────┤
│ MemorySaver         │ 内存             │ ✗ 否         │ 开发测试      │
│ (推荐用于开发)       │                  │              │ 短期应用      │
├─────────────────────┼──────────────────┼──────────────┼──────────────┤
│ SqliteSaver         │ SQLite 文件      │ ✓ 是         │ 单机部署      │
│ (推荐用于生产)       │                  │              │ 持久化需求    │
├─────────────────────┼──────────────────┼──────────────┼──────────────┤
│ PostgresSaver       │ PostgreSQL 数据库 │ ✓ 是        │ 分布式部署    │
│ (高级部署)           │                  │             │ 多进程共享    │
├─────────────────────┼──────────────────┼──────────────┼──────────────┤
│ MongoDBSaver        │ MongoDB          │ ✓ 是         │ 面向文档     │
│ (文档数据库)         │                  │              │ 灵活结构     │
└─────────────────────┴──────────────────┴──────────────┴──────────────┘

选择指南：

📌 开发阶段
   → 使用 MemorySaver
   原因: 配置简单，无需数据库，快速迭代

📌 生产单机部署
   → 使用 SqliteSaver
   原因: 轻量级，支持持久化，可靠性高

📌 生产分布式部署
   → 使用 PostgresSaver/MongoDBSaver
   原因: 多进程共享，支持水平扩展
""")

print()

# ===== 演示 7: 最佳实践 =====
print("="*70)
print("【演示 7】检查点使用最佳实践")
print("="*70)
print("""
✅ 推荐做法

1. 合理设置 thread_id
   ├─ 对话机器人: thread_id = user_id
   ├─ 工作流系统: thread_id = task_id
   ├─ 批处理: thread_id = batch_id
   └─ 优势: 数据隔离，支持并发

2. 定期清理检查点
   ├─ 删除过期的对话数据
   ├─ 释放存储空间
   └─ 提高查询性能

3. 监控检查点大小
   ├─ 对于长期对话，定期检查存储大小
   ├─ 可能需要归档历史数据
   └─ 防止存储溢出

4. 错误处理
   ├─ 捕获执行异常
   ├─ 检查点会保存当前状态
   └─ 可安全地重试失败步骤

❌ 避免的错误

1. 忘记设置 checkpointer
   → 无法支持断点续传和多轮对话

2. 对所有应用都使用 thread_id
   → 某些无状态应用不需要检查点

3. 检查点过大
   → 长期对话会导致数据膨胀
   → 定期清理是必要的

4. 混淆检查点和缓存
   → 检查点：保存执行状态
   → 缓存：避免重复计算
   → 两者用途不同！

═══════════════════════════════════════════════════════════════════════

快速参考

【配置】
    # MemorySaver
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()
    graph = graph.compile(checkpointer=checkpointer)

    # SqliteSaver（文件）
    from langgraph.checkpoint.sqlite import SqliteSaver
    checkpointer = SqliteSaver("./checkpoints.db")
    graph = graph.compile(checkpointer=checkpointer)

    # SqliteSaver（内存）
    checkpointer = SqliteSaver(":memory:")
    graph = graph.compile(checkpointer=checkpointer)

【调用】
    # 同一 session 的多次调用
    result = graph.invoke(
        input_data,
        config={"thread_id": "unique_session_id"}
    )

【优势】
    ✓ 支持多轮对话
    ✓ 支持断点续传
    ✓ 数据隔离和高并发
    ✓ 增强可靠性
    ✓ 完整的对话历史

【适用场景】
    • 多轮对话机器人
    • 工作流引擎
    • 任务调度系统
    • 长期运行的 Agent
    • 需要审计的业务流程
""")
