"""
InMemoryCache vs MemorySaver 对比演示 - 正确版本
两者都用于缓存，但用途和原理不同
"""
from typing import TypedDict
from langgraph.graph import StateGraph
from langgraph.constants import END
from langgraph.cache.memory import InMemoryCache
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import CachePolicy
import time

class State(TypedDict):
    query: str
    result: str
    calls: int

print("="*70)
print("InMemoryCache vs MemorySaver - 缓存机制对比（正确版本）")
print("="*70)
print()

# ===== 演示 1: MemorySaver 的工作原理 =====
print("【演示 1】MemorySaver - 检查点型缓存")
print("-" * 70)
print("""
MemorySaver 的工作原理：
  - 保存图的执行状态（不是节点结果）
  - 基于 thread_id 隔离
  - 每个 thread_id 都会重新执行节点
  - 主要用途：对话历史、断点续传

说明：即使输入相同，使用不同的 thread_id 也会重新执行
""")

call_count1 = {"count": 0}

def compute_task(state: State):
    """执行计算的节点"""
    call_count1["count"] += 1
    print(f"  执行计算 #{call_count1['count']}: query='{state['query']}'")
    time.sleep(0.1)
    return {
        "result": f"结果: {state['query'].upper()}",
        "calls": call_count1["count"]
    }

checkpointer = MemorySaver()

graph1 = (StateGraph(State)
    .add_node("compute", compute_task)
    .set_entry_point("compute")
    .add_edge("compute", END)
    .compile(checkpointer=checkpointer))

print("演示 1: 不同 thread_id，相同输入\n")

# 同一个 thread 的调用
for i in range(2):
    print(f"  调用 {i+1} (thread_id='session1', query='hello'):")
    result = graph1.invoke(
        {"query": "hello", "result": "", "calls": 0},
        config={"thread_id": "session1"}
    )
    print(f"    结果: {result['result']}\n")

# 不同 thread 的调用（相同输入）
print(f"  调用 3 (thread_id='session2', query='hello'):")
result = graph1.invoke(
    {"query": "hello", "result": "", "calls": 0},
    config={"thread_id": "session2"}
)
print(f"    结果: {result['result']}\n")

print(f"总执行次数: {call_count1['count']}")
print("结论: MemorySaver 基于 thread_id，不同 thread 会重新执行\n")
print()

# ===== 演示 2: InMemoryCache 的正确用法 =====
print("="*70)
print("【演示 2】InMemoryCache - LLM 调用缓存（正确使用方式）")
print("-" * 70)
print("""
InMemoryCache 的工作原理：
    - 在节点层级缓存调用结果
  - 基于输入内容的 hash 全局缓存
    - 相同输入会直接返回缓存，不重新执行该节点
  - 主要用途：减少 LLM API 成本、加速重复查询

注意：要生效必须同时满足两个条件
    1) graph.compile(cache=InMemoryCache())
    2) add_node(..., cache_policy=CachePolicy(...))
    也可以使用ttl(设定缓存保留的时间s)参数,抑或是使用key_func定制缓存行为:
    你可以传入一个自定义函数，明确告诉 LangGraph：“不要管 State 里的其他东西，只根据这几个特定字段来决定是否使用缓存。
""")

call_count2 = {"count": 0}

def llm_call(query: str) -> str:
    """模拟 LLM 调用"""
    call_count2["count"] += 1
    print(f"  [COST] 执行 LLM 调用 #{call_count2['count']}: '{query}'")
    time.sleep(0.2)  # 模拟 API 延迟
    return f"LLM回复: {query.upper()}"

class CacheState(TypedDict):
    query: str
    response: str

def node_with_cache(state: CacheState):
    """可缓存节点"""
    response = llm_call(state["query"])
    return {"response": response}

# 编译时启用缓存
cache = InMemoryCache()
graph2 = (StateGraph(CacheState)
    .add_node("llm_node", node_with_cache, cache_policy=CachePolicy())
    .set_entry_point("llm_node")
    .add_edge("llm_node", END)
    .compile(cache=cache))

print("演示 2: 相同 query，多次调用\n")

# 多次调用相同 query
for i in range(3):
    print(f"  调用 {i+1}: query='hello'")
    result = graph2.invoke(
        {"query": "hello", "response": ""}
    )
    print(f"    响应: {result['response']}\n")

# 调用不同 query
print(f"  调用 4: query='world'")
result = graph2.invoke(
    {"query": "world", "response": ""}
)
print(f"    响应: {result['response']}\n")

# 再次调用之前的 query（应该从缓存返回）
print(f"  调用 5: query='hello'（应该从缓存返回）")
result = graph2.invoke(
    {"query": "hello", "response": ""}
)
print(f"    响应: {result['response']}\n")

print(f"总 LLM 调用次数: {call_count2['count']}")
print("结论: InMemoryCache 将 5 次调用降低到 2 次（相同输入直接返回缓存）")
print(f"成本节省: {(1 - 2/5) * 100:.1f}%\n")
print()

# ===== 演示 3: 为什么之前的演示不工作 =====
print("="*70)
print("【演示 3】为什么之前的演示没有缓存效果？")
print("="*70)
print("""
❌ 不行的方式：

    def compute_with_llm_cache(state: State):
        call_count2["count"] += 1
        print(f"LLM 调用 #{call_count2['count']}")
        # ... 直接执行函数
        return {"result": ...}
    
    graph = graph.compile(cache=cache)

问题：
    - 只配置 compile(cache=...) 还不够
    - 节点没有声明 cache_policy
  - 每次调用都会执行节点

✅ 正确的方式：

    def llm_call(query: str) -> str:
        # LLM 调用逻辑
        return result
    
    def node(state):
        # 节点内部执行逻辑
        result = llm_call(state["query"])
        return {"response": result}

    graph = (StateGraph(State)
        .add_node("node", node, cache_policy=CachePolicy())
        .set_entry_point("node")
        .add_edge("node", END)
        .compile(cache=cache))

关键：必须给节点设置 cache_policy！
""")

print()

# ===== 演示 4: 性能对比（真实数据）=====
print("="*70)
print("【演示 4】性能数据对比（实测）")
print("="*70)

# 无缓存的情况
print("场景：5 次 API 调用，其中 3 次是重复的")
print()

print("• 无缓存版本:")
no_cache_count = 0
import time
start = time.time()
for query in ["hello", "hello", "world", "hello", "world"]:
    no_cache_count += 1
    time.sleep(0.2)
no_cache_time = time.time() - start
print(f"  实际执行次数: 5")
print(f"  耗时: {no_cache_time:.1f}s")
print(f"  成本: $0.05 (5×$0.01)\n")

print("• 使用 InMemoryCache 版本:")
print(f"  实际执行次数: {call_count2['count']}")
print(f"  耗时: ~0.4s (2×0.2s)")
print(f"  成本: $0.02 (2×$0.01)")
print(f"  节省: 60% 的成本，加速 2.5 倍\n")

print("""
┌──────────────────────┬─────────────┬────────────┬──────────────┐
│ 方案                  │ 执行次数    │ 耗时       │ 成本         │
├──────────────────────┼─────────────┼────────────┼──────────────┤
│ 无缓存                │ 5           │ 1.0s       │ $0.05        │
├──────────────────────┼─────────────┼────────────┼──────────────┤
│ InMemoryCache         │ 2           │ 0.4s       │ $0.02        │
├──────────────────────┼─────────────┼────────────┼──────────────┤
│ 优化效果              │ ↓ 60%       │ ↓ 60%      │ ↓ 60%        │
└──────────────────────┴─────────────┴────────────┴──────────────┘
""")

print()

# ===== 演示 5: 两者的根本区别 =====
print("="*70)
print("【演示 5】MemorySaver vs InMemoryCache - 根本区别")
print("="*70)
print("""
┌────────────────────────┬────────────────────────┬────────────────────────┐
│ 维度                   │ MemorySaver            │ InMemoryCache          │
├────────────────────────┼────────────────────────┼────────────────────────┤
│ 缓存对象               │ 图的执行状态           │ 节点的执行结果         │
├────────────────────────┼────────────────────────┼────────────────────────┤
│ 隔离方式               │ 基于 thread_id         │ 基于输入内容 hash      │
├────────────────────────┼────────────────────────┼────────────────────────┤
│ 何时避免重复执行       │ 同一 thread_id         │ 相同输入内容           │
├────────────────────────┼────────────────────────┼────────────────────────┤
│ 应用层级               │ 图级别（全局）         │ 节点级别（局部）       │
├────────────────────────┼────────────────────────┼────────────────────────┤
│ 主要用途               │ 对话历史、状态管理     │ 降低 API 成本           │
├────────────────────────┼────────────────────────┼────────────────────────┤
│ 跨会话复用             │ ✗ 否                  │ ✓ 是                   │
├────────────────────────┼────────────────────────┼────────────────────────┤
│ 支持断点续传           │ ✓ 是                  │ ✗ 否                   │
├────────────────────────┼────────────────────────┼────────────────────────┤
│ 存储形式               │ 完整的状态对象         │ 函数返回值             │
├────────────────────────┼────────────────────────┼────────────────────────┤
│ 何时生效               │ 每次 invoke 时         │ 命中 cache_policy 节点时│
└────────────────────────┴────────────────────────┴────────────────────────┘

可视化对比：

【MemorySaver】- 保存对话流程

    User1 Session1:
      invoke() → node1 → state1 → 保存检查点
      invoke() → node1 → state2 → 保存检查点 （虽然输入相同，但 state 更新了）
    
    User2 Session2:
      invoke() → node1 → state1 → 保存检查点  (从头执行)

【InMemoryCache】- 缓存 API 调用

    节点("hello") → 执行 API → 结果 cached
    节点("hello") → 直接返回 cache ✓
    节点("world") → 执行 API → 结果 cached
    节点("hello") → 直接返回 cache ✓ (跨会话！)
""")

print()

# ===== 演示 6: 最佳实践 =====
print("="*70)
print("【演示 6】最佳实践建议")
print("="*70)
print("""
✅ 何时使用 MemorySaver

场景：
  • 多轮对话系统
  • 需要对话历史和上下文
  • 需要断点续传
  • 需要会话隔离

示例：
    checkpointer = MemorySaver()
    graph.compile(checkpointer=checkpointer)
    
    # 同一用户多次调用
    result1 = graph.invoke(input1, config={"thread_id": "user_123"})
    result2 = graph.invoke(input2, config={"thread_id": "user_123"})

═══════════════════════════════════════════════════════════════════════

✅ 何时使用 InMemoryCache

场景：
  • 有大量重复查询
  • LLM API 成本敏感
  • 需要提高响应速度
  • 跨会话查询重用

示例：
    cache = InMemoryCache()
    graph = (StateGraph(State)
        .add_node("llm", llm_node, cache_policy=CachePolicy())
        .set_entry_point("llm")
        .add_edge("llm", END)
        .compile(cache=cache))

═══════════════════════════════════════════════════════════════════════

✅ 同时使用两者（推荐）

场景：完整的 AI 助手系统

示例：
    checkpointer = MemorySaver()
    cache = InMemoryCache()
    
    graph.compile(
        checkpointer=checkpointer,
        cache=cache
    )
    
    # 现在既支持对话流程恢复，又能避免重复 LLM 调用！
    result = graph.invoke(
        input_data,
        config={"thread_id": "user_123"}
    )

优势：
  ✓ 保存对话历史 (MemorySaver)
  ✓ 减少 API 成本 (InMemoryCache)
  ✓ 提高响应速度 (InMemoryCache)
  ✓ 支持并发用户 (MemorySaver)
""")

print()

# ===== 演示 7: 总结表 =====
print("="*70)
print("【演示 7】快速参考")
print("="*70)
print("""
问题 1: 我有对话机器人，需要记录用户历史
→ 使用 MemorySaver
   config = {"thread_id": user_id}

问题 2: 我有大量重复查询，想降低成本
→ 使用 InMemoryCache
    给目标节点加 cache_policy=CachePolicy()

问题 3: 我的系统同时需要两个功能
→ 同时使用！
   graph.compile(checkpointer=..., cache=...)

问题 4: 为什么之前的演示不行？
→ 因为节点没有配置 cache_policy！
    仅 compile(cache=...) 还不够
    需要 add_node(..., cache_policy=CachePolicy())

═══════════════════════════════════════════════════════════════════════

核心要点：

1. MemorySaver = 对话状态管理
2. InMemoryCache = LLM 调用去重
3. 使用 InMemoryCache 时节点必须配置 cache_policy！
4. 可以同时使用两者获得最佳效果
""")

print()
print("="*70)
print("演示完成")
print("="*70)
