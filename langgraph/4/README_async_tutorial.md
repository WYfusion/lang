# Python 异步（asyncio）说明教程

本文是面向你当前项目的异步实战教程，核心目标是：

- 读懂 `async/await` 的运行逻辑
- 避免 `await outside function` 等常见错误
- 会把同步代码改造成可运行的异步脚本

---

## 1. 为什么要用异步

在 AI Agent 场景中，常见耗时操作有：

- 请求大模型 API
- 调用外部 MCP 工具
- 网络 I/O（HTTP、数据库、WebSocket）

这些操作大多是 **I/O 密集型**。异步可以在等待 I/O 时切换任务，提升吞吐与响应效率。

---

## 2. 三个核心概念

### 2.1 协程函数（Coroutine Function）

用 `async def` 定义：

```python
async def foo():
    return "ok"
```

### 2.2 await

`await` 只能出现在 `async def` 内部，用于等待一个可等待对象。

```python
result = await some_async_call()
```

### 2.3 事件循环（Event Loop）

通过 `asyncio.run(main())` 启动整个异步程序。

```python
import asyncio

async def main():
    ...

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. 你遇到的典型错误

报错：

```text
SyntaxError: 'await' outside function
```

错误写法（顶层 `await`）：

```python
tools = await client.get_tools()
```

正确写法：

```python
async def main():
    tools = await client.get_tools()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. 从同步思维到异步思维

### 4.1 同步流程（串行阻塞）

1. 发请求
2. 等返回
3. 再发下一个

### 4.2 异步流程（等待时可切换）

1. 发起多个任务
2. 每个任务在等待 I/O 时让出执行权
3. 事件循环继续调度其他任务

---

## 5. 常用异步模式

### 5.1 单任务异步

```python
async def main():
    response = await agent.ainvoke(payload)
    print(response)
```

### 5.2 并发多个任务

```python
import asyncio

async def ask(agent, text):
    return await agent.ainvoke({"messages": [{"role": "user", "content": text}]})

async def main(agent):
    tasks = [
        ask(agent, "北京天气"),
        ask(agent, "上海天气"),
        ask(agent, "广州天气"),
    ]
    results = await asyncio.gather(*tasks)
    for r in results:
        print(r["messages"][-1].content)
```

> `asyncio.gather` 适合并发等待多个 I/O 任务。

### 5.3 控制并发量（避免打爆接口）

```python
import asyncio

sem = asyncio.Semaphore(3)

async def limited_call(coro):
    async with sem:
        return await coro
```

---

## 6. 在 Agent + MCP 中怎么落地

以你当前场景为例，异步链路通常是：

1. `tools = await client.get_tools()`
2. `agent = create_agent(...)`
3. `response = await agent.ainvoke(...)`

其中第 1、3 步都是异步调用。

最小模板：

```python
import asyncio

async def main():
    tools = await client.get_tools()
    agent = create_agent(llm, tools=tools)
    response = await agent.ainvoke(payload)
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 7. 异步代码调试技巧

- 在关键步骤前后打印日志（例如“开始加载工具”“开始调用模型”）
- 给外部调用加超时（如 `asyncio.wait_for`）
- `gather` 时用 `return_exceptions=True` 收集异常，避免一个任务失败导致整体中断

示例：

```python
results = await asyncio.gather(*tasks, return_exceptions=True)
for item in results:
    if isinstance(item, Exception):
        print("任务失败:", item)
```

---

## 8. 异步常见坑速查

1. **顶层 await**：必须移入 `async def`
2. **忘记 `asyncio.run`**：主协程不会执行
3. **同步阻塞混入异步**：`time.sleep()` 应改为 `await asyncio.sleep()`
4. **CPU 密集任务误用异步**：应交给多进程或线程池
5. **并发过大**：需要信号量限流

---

## 9. 一个完整可运行小例子

```python
import asyncio

async def worker(name, delay):
    print(f"{name} 开始")
    await asyncio.sleep(delay)
    print(f"{name} 完成")
    return f"{name} done"

async def main():
    tasks = [worker("A", 1), worker("B", 2), worker("C", 1.5)]
    results = await asyncio.gather(*tasks)
    print("结果:", results)

if __name__ == "__main__":
    asyncio.run(main())
```

你会看到 A/B/C 交错执行，这就是异步调度的直观表现。

---

## 10. 学习路径建议

1. 先熟悉 `async def / await / asyncio.run`
2. 再掌握 `gather` 与异常处理
3. 最后结合 Agent + MCP 做并发任务与限流控制

---

## 11. 一句话总结

**异步不是让代码“更快执行”，而是让程序“更高效等待”。** 在你这个 Agent 场景里，异步是默认推荐方案。
