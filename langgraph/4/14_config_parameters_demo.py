"""
LangGraph config 参数详解
config 字典可以传入多个参数来控制图的执行行为
"""
from typing import TypedDict
from langgraph.graph import StateGraph
from langgraph.constants import END
from langgraph.checkpoint.memory import MemorySaver
import time

class SimpleState(TypedDict):
    value: int
    step_count: int

print("="*70)
print("LangGraph config 参数详解")
print("="*70)
print()

# ===== 演示 1: thread_id 参数 =====
print("【演示 1】thread_id - 会话标识")
print("-" * 70)
print("""
作用：
  - 标识一个独立的执行线程/会话
  - 配合 checkpointer，保存和恢复状态
  - 不同 thread_id 的执行相互隔离

类型：str

示例：
    config={"thread_id": "user_123"}
    config={"thread_id": "conversation_abc"}
    config={"thread_id": "task_001"}

使用场景：
  ✓ 多轮对话机器人
  ✓ 长期任务管理
  ✓ 用户会话跟踪
  
注意：
  - 必须配合 checkpointer 使用才能生效
  - 没有设置 checkpointer 时，thread_id 无效
""")

print()

# ===== 演示 2: recursion_limit 参数 =====
print("="*70)
print("【演示 2】recursion_limit - 递归深度限制")
print("-" * 70)
print("""
作用：
  - 限制图执行的最大步数
  - 防止无限循环或过长执行
  - 当超过限制时抛出异常

类型：int，default=25

示例：
    config={"recursion_limit": 10}
    config={"recursion_limit": 100}
    config={"recursion_limit": 1000}

行为演示：
""")

def step_node_a(state: SimpleState):
    """模拟执行步骤"""
    print(f"  → 执行 Node A, 当前步数: {state['step_count']}")
    return {"step_count": state["step_count"] + 1, "value": state["value"] + 1}

def step_node_b(state: SimpleState):
    """模拟执行步骤"""
    print(f"  → 执行 Node B, 当前步数: {state['step_count']}")
    return {"step_count": state["step_count"] + 1, "value": state["value"] + 1}

def should_continue(state: SimpleState):
    """条件判断：继续循环还是停止"""
    if state["step_count"] < 5:
        return "continue"
    return END

# 构建带循环的图
graph = (StateGraph(SimpleState)
    .add_node("A", step_node_a)
    .add_node("B", step_node_b)
    .set_entry_point("A")
    .add_edge("A", "B")
    .add_conditional_edges(
        "B",
        should_continue,
        {
            "continue": "A",
            END: END
        }
    )
    .compile())

print("• 不限制递归深度（默认 25）:")
try:
    result = graph.invoke(
        {"value": 0, "step_count": 0},
        config={}
    )
    print(f"  ✅ 执行成功，总步数: {result['step_count']}\n")
except Exception as e:
    print(f"  ❌ 异常: {e}\n")

print("• 限制递归深度为 3（会超限）:")
try:
    result = graph.invoke(
        {"value": 0, "step_count": 0},
        config={"recursion_limit": 3}
    )
    print(f"  ✅ 执行成功，总步数: {result['step_count']}\n")
except Exception as e:
    print(f"  ❌ 异常: {type(e).__name__}: {str(e)[:60]}...\n")

print("• 限制递归深度为 10（足够完成）:")
try:
    result = graph.invoke(
        {"value": 0, "step_count": 0},
        config={"recursion_limit": 10}
    )
    print(f"  ✅ 执行成功，总步数: {result['step_count']}\n")
except Exception as e:
    print(f"  ❌ 异常: {e}\n")

print("""
应用场景：
  ✓ 防止无限循环
  ✓ 控制执行时间和资源消耗
  ✓ 设置不同用户的执行限制

推荐做法：
  - 根据图的复杂度调整
  - 一般 25-100 足够
  - 复杂工作流可设置 500-1000
""")

print()

# ===== 演示 3: debug 参数 =====
print("="*70)
print("【演示 3】debug - 调试模式")
print("-" * 70)
print("""
作用：
  - 启用详细的调试输出
  - 显示每个节点的输入/输出
  - 便于诊断问题

类型：bool，default=False

示例：
    config={"debug": True}
    config={"debug": False}

演示：启用调试模式
""")

simple_graph = (StateGraph(SimpleState)
    .add_node("step1", lambda s: {"value": s["value"] + 10, "step_count": 1})
    .add_node("step2", lambda s: {"value": s["value"] * 2, "step_count": 2})
    .set_entry_point("step1")
    .add_edge("step1", "step2")
    .add_edge("step2", END)
    .compile())

print("不启用调试:")
result = simple_graph.invoke(
    {"value": 5, "step_count": 0},
    config={"debug": False}
)
print(f"最终结果: {result}\n")

print("启用调试（详细日志）:")
result = simple_graph.invoke(
    {"value": 5, "step_count": 0},
    config={"debug": True}
)
print(f"最终结果: {result}\n")

print("""
应用场景：
  ✓ 开发和测试阶段
  ✓ 问题诊断
  ✓ 理解执行流程
  ✗ 生产环境不建议启用（会产生大量日志）
""")

print()

# ===== 演示 4: tags 参数 =====
print("="*70)
print("【演示 4】tags - 标签（用于追踪）")
print("-" * 70)
print("""
作用：
  - 为执行添加标签
  - 用于日志追踪和分析
  - 便于按类型统计执行情况

类型：list[str]

示例：
    config={"tags": ["important", "user_123"]}
    config={"tags": ["test", "batch_001"]}
    config={"tags": ["high_priority", "payment"]}

演示：
""")

# 假设有日志系统可以收集这些标签
test_cases = [
    {"tags": ["test", "unit_test"], "description": "单元测试"},
    {"tags": ["production", "user_request"], "description": "用户请求"},
    {"tags": ["internal", "maintenance"], "description": "内部维护"},
]

for test_case in test_cases:
    print(f"执行: {test_case['description']}")
    result = simple_graph.invoke(
        {"value": 1, "step_count": 0},
        config={"tags": test_case["tags"]}
    )
    print(f"  标签: {test_case['tags']}")
    print(f"  结果: {result}\n")

print("""
应用场景：
  ✓ 日志和监控
  ✓ 性能分析
  ✓ 请求分类
  ✓ 故障排查

推荐标签：
  - 环境: test, staging, production
  - 优先级: high, medium, low
  - 用户: user_id, batch_id
  - 功能: search, payment, analysis
""")

print()

# ===== 演示 5: metadata 参数 =====
print("="*70)
print("【演示 5】metadata - 元数据（附加信息）")
print("-" * 70)
print("""
作用：
  - 携带额外的上下文信息
  - 传递请求元数据
  - 便于后续追踪和分析

类型：dict

示例：
    config={"metadata": {"user_id": "123", "session": "abc"}}
    config={"metadata": {"source": "api", "version": "v1"}}
    config={"metadata": {"request_id": "req_456", "timestamp": "2024-01-01"}}

演示：
""")

metadata_examples = [
    {
        "metadata": {
            "user_id": "user_123",
            "request_id": "req_001",
            "source": "web"
        },
        "description": "Web API 请求"
    },
    {
        "metadata": {
            "user_id": "user_456",
            "request_id": "req_002",
            "source": "mobile",
            "client_version": "2.0"
        },
        "description": "移动应用请求"
    },
]

for example in metadata_examples:
    print(f"请求类型: {example['description']}")
    result = simple_graph.invoke(
        {"value": 1, "step_count": 0},
        config={"metadata": example["metadata"]}
    )
    print(f"  元数据: {example['metadata']}")
    print(f"  结果: {result}\n")

print("""
应用场景：
  ✓ 请求追踪（request_id）
  ✓ 用户上下文（user_id）
  ✓ 来源识别（source）
  ✓ 版本控制（version）
  ✓ 时间戳记录
""")

print()

# ===== 演示 6: configurable 参数 =====
print("="*70)
print("【演示 6】configurable - 可配置参数（高级）")
print("-" * 70)
print("""
作用：
  - 动态配置图的行为
  - 需要图在定义时支持可配置项
  - 不同调用可传入不同配置

类型：dict

示例：
    config={"configurable": {"model": "gpt-4"}}
    config={"configurable": {"temperature": 0.7, "max_tokens": 100}}
    config={"configurable": {"enable_cache": True}}

说明：
  - 这个参数需要在图定义时显式支持
  - 一般用于 RunnableConfig 中
  - 允许灵活调整图的执行参数

演示：(需要特殊的图定义，这里仅展示概念)
""")

print("""
应用场景：
  ✓ 不同用户使用不同模型
  ✓ A/B 测试不同策略
  ✓ 动态调整参数
  ✓ 多租户系统的定制化
""")

print()

# ===== 演示 7: config 参数总结 =====
print("="*70)
print("【演示 7】config 参数完整参考")
print("="*70)
print("""
┌─────────────────┬──────────┬─────────┬────────────────────────────────┐
│ 参数名          │ 类型     │ 必需    │ 说明                           │
├─────────────────┼──────────┼─────────┼────────────────────────────────┤
│ thread_id       │ str      │ ✗ 可选  │ 会话/线程标识                  │
│                 │          │         │ 用途: 多轮对话、断点续传       │
├─────────────────┼──────────┼─────────┼────────────────────────────────┤
│ recursion_limit │ int      │ ✗ 可选  │ 最大执行步数                   │
│                 │          │         │ 默认: 25，防止无限循环        │
├─────────────────┼──────────┼─────────┼────────────────────────────────┤
│ debug           │ bool     │ ✗ 可选  │ 启用调试模式                   │
│                 │          │         │ 默认: False，显示详细日志     │
├─────────────────┼──────────┼─────────┼────────────────────────────────┤
│ tags            │ list[str]│ ✗ 可选  │ 执行标签                       │
│                 │          │         │ 用途: 追踪、分类、统计        │
├─────────────────┼──────────┼─────────┼────────────────────────────────┤
│ metadata        │ dict     │ ✗可选   │ 元数据信息                     │
│                 │          │         │ 用途: 请求追踪、上下文        │
├─────────────────┼──────────┼─────────┼────────────────────────────────┤
│ configurable    │ dict     │ ✗ 可选  │ 动态配置参数                   │
│                 │          │         │ 用途: 灵活调整执行行为        │
└─────────────────┴──────────┴─────────┴────────────────────────────────┘

常见组合用法：
""")

print("""
【场景 1】多轮对话机器人
    config = {
        "thread_id": "user_123",
        "recursion_limit": 50,
        "tags": ["chatbot", "production"],
        "metadata": {
            "user_id": "user_123",
            "session": "conv_abc"
        }
    }

【场景 2】API 服务
    config = {
        "recursion_limit": 30,
        "debug": False,
        "tags": ["api", "v1"],
        "metadata": {
            "request_id": "req_001",
            "source": "web_api",
            "timestamp": "2024-01-01T12:00:00"
        }
    }

【场景 3】批处理任务
    config = {
        "thread_id": "batch_001",
        "recursion_limit": 100,
        "tags": ["batch", "data_processing"],
        "metadata": {
            "batch_id": "batch_001",
            "total_items": 1000,
            "priority": "high"
        }
    }

【场景 4】开发调试
    config = {
        "debug": True,
        "recursion_limit": 10,
        "tags": ["debug", "development"],
        "metadata": {"developer": "me"}
    }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 最佳实践：

1. 总是设置 recursion_limit
   → 防止意外的无限循环

2. 生产环境设置 thread_id
   → 支持会话管理和断点续传
   → 需要配合 checkpointer 使用

3. 集成 tags 和 metadata
   → 便于监控、日志、追踪
   → 帮助问题诊断

4. 开发时启用 debug
   → 理解执行流程
   → 生产环境关闭

❌ 常见错误：

1. 设置了 thread_id 但没有配置 checkpointer
   → thread_id 无效，状态无法保存

2. 忽略 recursion_limit
   → 可能导致执行时间过长或无限循环

3. 过度使用 debug
   → 大量日志产生，降低性能

4. metadata 储存过多数据
   → 可能导致内存溢出或性能问题
""")

print()
print("="*70)
print("演示完成")
print("="*70)
