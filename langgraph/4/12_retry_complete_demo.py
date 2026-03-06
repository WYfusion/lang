"""
LangGraph 重试机制完整演示 - 使用正确的 RetryPolicy API
"""
from typing import TypedDict
from langgraph.graph import StateGraph
from langgraph.constants import END
from langgraph.types import RetryPolicy
import time

class State(TypedDict):
    value: str
    attempts: int

print("="*70)
print("LangGraph 重试机制演示 - RetryPolicy 正确用法")
print("="*70)
print()

# ===== 演示 1: 基础重试 =====
print("【演示 1】基础重试 - 自动重试失败的节点")
print("-" * 70)

attempt_tracker = {}

def simulate_flaky_operation(state: State):
    """模拟一个不稳定的操作（前两次失败，第三次成功）"""
    
    key = "attempt_1"
    attempt_tracker[key] = attempt_tracker.get(key, 0) + 1
    current_attempt = attempt_tracker[key]
    
    print(f"  🔄 尝试 #{current_attempt}: 执行不稳定的操作")
    
    if current_attempt < 3:
        print(f"    ❌ 失败（模拟错误）")
        raise RuntimeError(f"操作失败 - 第 {current_attempt} 次尝试")
    else:
        print(f"    ✅ 成功！")
        return {
            "value": state["value"] + " -> Recovered",
            "attempts": current_attempt
        }

def finalize(state: State):
    print(f"  ✓ 执行最终步骤")
    return {
        "value": state["value"] + " -> Finalized",
        "attempts": state["attempts"]
    }

# 构建图表 - 配置重试策略
print("\n📋 配置 RetrPolicy:")
print("   initial_interval=0.1 秒")
print("   backoff_factor=2.0")
print("   max_interval=1.0 秒")
print("   max_attempts=3 （1次初始 + 2次重试）")
print()

retry_policy = RetryPolicy(
    initial_interval=0.1,      # 第一次重试延迟 0.1 秒
    backoff_factor=2.0,        # 延迟倍增因子
    max_interval=1.0,          # 最大延迟 1 秒
    max_attempts=3             # 最多 3 次尝试
)

graph1 = (StateGraph(State)
    .add_node("risky", simulate_flaky_operation, retry_policy=retry_policy)
    .add_node("finalize", finalize)
    .set_entry_point("risky")
    .add_edge("risky", "finalize")
    .add_edge("finalize", END)
    .compile())

print("执行图表...\n")
try:
    result1 = graph1.invoke({"value": "Start", "attempts": 0})
    print(f"\n✅ 执行成功！")
    print(f"   最终值: {result1['value']}")
    print(f"   总尝试: {result1['attempts']}")
except Exception as e:
    print(f"\n❌ 执行失败: {e}")
    print(f"   总尝试: {attempt_tracker.get('attempt_1', 0)}")

print()

# ===== 演示 2: 只重试特定异常 =====
print("="*70)
print("【演示 2】条件重试 - 只重试特定异常")
print("-" * 70)

class TemporaryError(Exception):
    """临时错误，应该重试"""
    pass

class PermanentError(Exception):
    """永久错误，不应该重试"""
    pass

attempt_tracker2 = {"count": 0}

def selective_retry_node(state: State):
    attempt_tracker2["count"] += 1
    print(f"  🔄 尝试 #{attempt_tracker2['count']}")
    
    if attempt_tracker2["count"] < 2:
        print(f"    ❌ 临时错误（会重试）")
        raise TemporaryError("网络超时...")
    else:
        print(f"    ✅ 成功")
        return {"value": state["value"] + " -> Recovered", "attempts": attempt_tracker2["count"]}

# 只重试 TemporaryError，不重试 PermanentError
retry_policy2 = RetryPolicy(
    max_attempts=3,
    retry_on=TemporaryError  # 只重试这个异常类型
)

graph2 = (StateGraph(State)
    .add_node("selective", selective_retry_node, retry_policy=retry_policy2)
    .set_entry_point("selective")
    .add_edge("selective", END)
    .compile())

print("📋 配置: 只重试 TemporaryError\n")
print("执行图表...\n")
try:
    result2 = graph2.invoke({"value": "Start", "attempts": 0})
    print(f"\n✅ 执行成功!")
    print(f"   最终值: {result2['value']}")
except Exception as e:
    print(f"\n❌ 执行失败: {type(e).__name__}: {e}")

print()

# ===== 演示 3: 不同的重试策略对比 =====
print("="*70)
print("【演示 3】重试策略对比")
print("-" * 70)

configs = [
    {
        "name": "激进重试",
        "policy": RetryPolicy(
            initial_interval=0.01,
            backoff_factor=1.5,
            max_interval=0.5,
            max_attempts=5
        )
    },
    {
        "name": "保守重试",
        "policy": RetryPolicy(
            initial_interval=0.5,
            backoff_factor=3.0,
            max_interval=10.0,
            max_attempts=2
        )
    },
    {
        "name": "标准重试（推荐）",
        "policy": RetryPolicy(
            initial_interval=0.1,
            backoff_factor=2.0,
            max_interval=5.0,
            max_attempts=3
        )
    }
]

print("\n三种主要的重试策略对比：\n")
for config in configs:
    policy = config["policy"]
    print(f"📌 {config['name']}")
    print(f"   initial_interval: {policy.initial_interval}s")
    print(f"   backoff_factor: {policy.backoff_factor}")
    print(f"   max_interval: {policy.max_interval}s")
    print(f"   max_attempts: {policy.max_attempts}")
    print()

print("="*70)
print("📚 RetryPolicy 参数说明")
print("="*70)
print("""
1️⃣  initial_interval (float) - 秒
    ├─ 第一次重试前的延迟时间
    ├─ 默认值: 0.5 秒
    └─ 使用场景: 网络请求推荐 0.1-0.5 秒

2️⃣  backoff_factor (float)
    ├─ 延迟的倍增因子（指数退避）
    ├─ 默认值: 2.0
    ├─ 延迟序列: 0.1s -> 0.2s -> 0.4s -> 0.8s...
    └─ 使用场景: 2.0 最常见，1.5 更温和，3.0 更激进

3️⃣  max_interval (float) - 秒
    ├─ 最大延迟时间上限
    ├─ 默认值: 128.0 秒
    └─ 使用场景: 防止延迟过长，通常设为 5-30 秒

4️⃣  max_attempts (int)
    ├─ 最大尝试次数（包括初始尝试）
    ├─ 默认值: 3
    ├─ max_attempts=3 表示: 1次初始 + 2次重试
    └─ 使用场景: 3-5 比较合理

5️⃣  jitter (bool)
    ├─ 是否添加随机抖动（0-25% 范围）
    ├─ 默认值: True
    └─ 用途: 避免惊群效应（多个任务同时重试）

6️⃣  retry_on (callable or exception type)
    ├─ 哪些异常需要重试
    ├─ 默认值: 所有异常
    ├─ 例: retry_on=TimeoutError
    └─ 例: retry_on=[TimeoutError, ConnectionError]

═══════════════════════════════════════════════════════════════════════

🎯 使用建议

【网络请求】➜ 激进重试
retry_policy = RetryPolicy(
    initial_interval=0.1,
    backoff_factor=2.0,
    max_interval=5.0,
    max_attempts=3
)

【数据库操作】➜ 标准重试
retry_policy = RetryPolicy(
    initial_interval=0.5,
    backoff_factor=2.0,
    max_interval=10.0,
    max_attempts=2
)

【外部服务调用】➜ 保守重试
retry_policy = RetryPolicy(
    initial_interval=1.0,
    backoff_factor=3.0,
    max_interval=30.0,
    max_attempts=2
)

【特定异常重试】
retry_policy = RetryPolicy(
    max_attempts=3,
    retry_on=[TimeoutError, ConnectionError]
)

═══════════════════════════════════════════════════════════════════════

💡 何时使用重试？

✅ 应该重试:
   • 网络连接超时
   • 临时的服务不可用
   • 并发冲突导致的失败
   • 资源暂时锁定

❌ 不应该重试:
   • 权限错误 (403, 401)
   • 资源不存在 (404)
   • 代码逻辑错误
   • 数据验证失败
""")
