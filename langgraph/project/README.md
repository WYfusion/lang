# LangGraph 企业级流式语音对话系统 — 学习教程

> 一个完整的企业级 LangGraph 项目框架，涵盖流式语音对话、RAG 检索增强、多 Agent 协同、长期记忆管理等核心能力。

---

## 📁 项目结构总览

```
langgraph/7/
├── main.py                         # FastAPI 应用入口 (Lifespan 管理)
├── pyproject.toml                  # 依赖管理
├── config/
│   └── settings.py                 # Pydantic Settings 集中配置
├── schemas/                        # Pydantic 数据模型 (API 层)
│   ├── message.py                  # 消息 Schema
│   ├── conversation.py             # 会话 Schema
│   ├── memory.py                   # 记忆 Schema
│   ├── voice.py                    # 语音 Schema (WebSocket协议)
│   └── rag.py                      # RAG Schema
├── db/                             # 数据库层
│   ├── base.py                     # SQLAlchemy 2.0 异步引擎 + Base
│   ├── models/                     # ORM 模型
│   │   ├── conversation.py         # 会话表
│   │   ├── message.py              # 消息表
│   │   └── memory.py               # 长期记忆表
│   ├── repositories/               # 仓储模式 (CRUD)
│   │   ├── conversation_repo.py
│   │   ├── message_repo.py
│   │   └── memory_repo.py
│   └── alembic/                    # 数据库迁移
│       ├── alembic.ini
│       ├── env.py                  # 异步迁移引擎
│       └── versions/
├── graph/                          # ★ LangGraph 核心层
│   ├── state.py                    # 图的 State 定义 (TypedDict + Reducer)
│   ├── main_graph.py              # 主编排图 (StateGraph 构建)
│   ├── nodes/                      # 图的节点
│   │   ├── input_processor.py      # 输入预处理 (文本/语音统一)
│   │   ├── memory_loader.py        # 记忆加载
│   │   ├── router.py               # 意图路由 (LLM structured output)
│   │   ├── chat.py                 # 对话节点 (LCEL 链)
│   │   ├── rag_retriever.py        # RAG 检索节点
│   │   ├── voice_processor.py      # TTS 合成节点
│   │   ├── response_synthesizer.py # 响应合成
│   │   ├── memory_updater.py       # 记忆提取与更新
│   │   └── tool_executor.py        # 工具执行节点
│   ├── edges/
│   │   └── conditions.py           # 条件边 (动态路由)
│   └── subgraphs/                  # 子图
│       ├── rag_subgraph.py         # RAG 子图 (改写→检索→评估→生成)
│       ├── voice_subgraph.py       # 语音子图 (降噪→VAD→STT)
│       └── multi_agent_subgraph.py # 多Agent子图 (Supervisor模式)
├── agents/                         # Agent 实现
│   ├── base_agent.py               # Agent 基类
│   ├── supervisor.py               # Supervisor Agent (调度)
│   ├── researcher.py               # 研究 Agent
│   ├── writer.py                   # 写作 Agent
│   └── voice_agent.py              # 语音 Agent
├── tools/                          # LangChain Tools
│   ├── registry.py                 # 工具注册表
│   ├── search_tool.py              # Web 搜索
│   ├── voice_tools/                # 语音工具集
│   │   ├── stt.py                  # 语音转文字
│   │   ├── tts.py                  # 文字转语音
│   │   ├── noise_reduction.py      # 降噪算法
│   │   └── vad.py                  # 语音活动检测
│   ├── rag_tools/
│   │   ├── document_loader.py      # 文档加载
│   │   └── retriever.py            # 向量检索
│   └── memory_tools/
│       └── memory_store.py         # 记忆存储/检索
├── rag/                            # RAG 模块
│   ├── vectorstore.py              # 向量存储管理 (Chroma/FAISS)
│   ├── chunker.py                  # 文档分块策略
│   ├── embeddings.py               # Embedding 模型管理
│   └── retrieval_chain.py          # ★ LCEL 检索链
├── memory/                         # 记忆管理
│   ├── short_term.py               # 短期记忆 (消息窗口)
│   ├── long_term.py                # 长期记忆 (LLM提取+向量化)
│   └── memory_chain.py             # LCEL 记忆链
├── voice/                          # 语音处理
│   ├── stream_handler.py           # WebSocket 流式语音处理器
│   ├── audio_processor.py          # 音频处理管线
│   └── codec.py                    # 音频编解码
├── api/                            # API 层
│   ├── deps.py                     # FastAPI 依赖注入
│   ├── middleware.py               # 中间件 (日志/异常)
│   ├── v1/
│   │   ├── router.py               # 路由汇总
│   │   ├── chat.py                 # 对话API (REST + SSE)
│   │   ├── voice.py                # 语音API
│   │   ├── memory.py               # 记忆管理API
│   │   └── rag.py                  # RAG管理API
│   └── websocket/
│       └── voice_stream.py         # ★ WebSocket 语音流端点
├── services/                       # 服务层
│   ├── llm_service.py              # LLM 工厂 (多Provider)
│   ├── conversation_service.py     # 会话服务
│   └── graph_service.py            # ★ Graph 执行服务
└── utils/
    ├── logging.py                  # structlog 结构化日志
    ├── exceptions.py               # 自定义异常体系
    └── callbacks.py                # LangChain 回调处理器
```

---

## 🎓 核心教程要点

### 1. LangGraph State 设计 (`graph/state.py`)

```python
from langgraph.graph.message import add_messages

class MainGraphState(TypedDict, total=False):
    # Reducer: messages 自动追加, 不覆盖
    messages: Annotated[list[BaseMessage], add_messages]
    
    # 直接覆盖: 每个节点更新自己负责的字段
    current_intent: str
    response_text: str
```

**核心概念:**
- `Annotated[list, add_messages]` — Reducer 模式, 节点返回的消息自动追加到列表
- 无 Reducer 的字段 — 直接覆盖语义
- `total=False` — 所有字段可选, 节点只需返回部分更新

### 2. 主编排图 (`graph/main_graph.py`)

```
START → 输入预处理 → 记忆加载 → 意图路由 ─┬→ 对话节点
                                          ├→ RAG子图
                                          ├→ 工具执行
                                          └→ 多Agent子图
                                               ↓
                              响应合成 ← ─────┘
                                  ↓
                              记忆更新 →(语音?)→ TTS → END
                                  ↓ (文本)
                                 END
```

**关键 API:**
- `StateGraph(State)` — 创建图
- `graph.add_node(name, func)` — 注册节点
- `graph.add_edge(a, b)` — 无条件边
- `graph.add_conditional_edges(node, func, mapping)` — 条件边
- `graph.compile(checkpointer=...)` — 编译 + 持久化


架构层级
层级	目录	核心职责
入口	main.py	FastAPI + Lifespan 生命周期管理
配置	config/settings.py	Pydantic Settings 多环境配置
Schema	schemas/	Pydantic V2 数据模型 (消息/会话/记忆/语音/RAG)
数据库	db/	SQLAlchemy 2.0 异步 ORM + Alembic 迁移 + Repository 模式
★ Graph	graph/	LangGraph 主编排图 + State + 节点 + 条件边 + 子图
Agent	agents/	Supervisor 多 Agent 协作架构
Tool	tools/	工具注册表 + 语音/RAG/记忆工具集
RAG	rag/	向量存储 + 分块 + LCEL 检索链
记忆	memory/	短期窗口 + 长期记忆(LLM提取+向量检索)
语音	voice/	WebSocket 流式处理 + 降噪/VAD/STT/TTS 管线
API	api/	REST + SSE 流式 + WebSocket 语音流
服务	services/	LLM 工厂(多 Provider) + Graph 执行服务
核心教程亮点
每个文件都包含详细的 教程要点注释，重点覆盖：

State 设计 — add_messages Reducer 与字段覆盖语义
LCEL 链 — prompt | llm.with_structured_output() | parser 模式
流式输出 — astream_events(version="v2") token 级流式
Checkpoint — MemorySaver / SqliteSaver 会话恢复
条件边路由 — LLM structured output 驱动的意图路由
子图封装 — RAG 子图 / 语音子图 / 多 Agent 子图
语音降噪 — noisereduce 频谱减法 + WebRTC VAD
所有代码都预留了 TODO 标记，具体业务逻辑待后续填充实现。

### 3. LCEL 典型模式 (`rag/retrieval_chain.py`, `graph/nodes/chat.py`)

```python
# 基础 RAG 链
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 意图路由链
router_chain = prompt | llm.with_structured_output(RouterOutput)

# 记忆提取链
extract_chain = prompt | llm.with_structured_output(MemoryExtraction)
```

### 4. 流式输出 (`services/graph_service.py`, `api/v1/chat.py`)

```python
# LangGraph astream_events — token 级流式
async for event in graph.astream_events(state, config, version="v2"):
    if event["event"] == "on_chat_model_stream":
        token = event["data"]["chunk"].content
        yield f"data: {json.dumps({'event': 'token', 'delta': token})}\n\n"
```

### 5. WebSocket 语音流 (`api/websocket/voice_stream.py`)

```
客户端 ──Audio Binary───→ 服务端
客户端 ←──JSON Events────→ 服务端 (stt_final, llm_token, ...)
客户端 ←──Audio Binary───→ 服务端 (TTS chunks)
```

### 6. 多 Agent 协作 (`graph/subgraphs/multi_agent_subgraph.py`)

```
Supervisor → 分配任务 → Worker Agent → 返回结果 → Supervisor → ... → 综合
```

### 7. Checkpoint 持久化

```python
# 开发环境
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# 生产环境
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
checkpointer = AsyncSqliteSaver.from_conn_string("./data/checkpoints.db")

graph.compile(checkpointer=checkpointer)

# 恢复会话: 通过 thread_id
config = {"configurable": {"thread_id": "existing_thread_id"}}
result = await graph.ainvoke(new_state, config)  # 自动恢复历史
```

### 8. 数据库 + Alembic 迁移

```bash
# 生成迁移
alembic revision --autogenerate -m "initial tables"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

---

## 🚀 启动方式

```bash
# 安装依赖
pip install -e ".[dev]"

# 启动开发服务器
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# API 文档
# http://localhost:8000/docs
```

---

## 🏗️ 架构设计原则

| 层级 | 职责 | 关键技术 |
|------|------|----------|
| API | HTTP/WS 接入 | FastAPI, SSE, WebSocket |
| Service | 业务编排 | GraphService, ConversationService |
| Graph | 流程编排 | LangGraph StateGraph, Subgraph |
| Agent | 智能决策 | Supervisor, create_react_agent |
| Tool | 能力扩展 | @tool, StructuredTool |
| RAG | 知识检索 | LCEL Chain, VectorStore |
| Memory | 记忆管理 | Short-term + Long-term |
| Voice | 语音处理 | STT, TTS, VAD, 降噪 |
| DB | 持久化 | SQLAlchemy 2.0 async, Alembic |
| Config | 配置管理 | Pydantic Settings |

---

## 📌 企业级实践清单

- [x] Pydantic V2 强类型 Schema
- [x] SQLAlchemy 2.0 异步 ORM + Alembic 迁移
- [x] Repository 模式隔离数据层
- [x] FastAPI 依赖注入
- [x] 结构化日志 (structlog)
- [x] 统一异常处理
- [x] LLM with_retry + with_fallbacks
- [x] 多 Provider 支持 (OpenAI/DashScope/智谱/DeepSeek)
- [x] LangGraph Checkpoint 持久化
- [x] SSE 流式输出
- [x] WebSocket 实时语音
- [x] 工具注册表 (Tool Registry)
- [x] 多 Agent Supervisor 模式
- [x] RAG 完整管线 (改写→检索→评估→生成)
- [x] 长期记忆 (LLM提取 + 向量检索)
- [x] 语音降噪 / VAD / STT / TTS 工具链
