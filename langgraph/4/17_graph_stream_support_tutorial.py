"""
LangGraph 图的 Stream 支持教学脚本

模块主题：
1. 对比 `invoke`（一次性返回）与 `stream`（增量返回）的行为差异。
2. 讲清楚 `stream_mode="updates"` 与 `stream_mode="values"` 的常见企业用法。
3. 演示如何把流式事件接入“企业级消费层”（审计、脱敏、容错）。

核心讲解点：
1. Stream 的本质：节点执行过程中持续产出可观测事件，而不是等待全流程结束。
2. 模式选择：`updates` 更轻量，`values` 更直观，按场景选型。
3. 工程规范：稳定事件格式、状态最小暴露、日志可追踪、异常可回放。
4. 复用思路：统一封装 `consume_stream_with_audit`，降低业务方接入成本。


注意这里的stream和LLM的streaming输出是两个不同层面的概念:
核心区别在于“事件粒度”，不是“LLM token 流”。

stream_mode="updates"：每执行完一个节点（或触发一次状态合并）就吐出“增量事件”——只包含该步新增/改动的字段。例如 {"node": "route", "route": "analysis", "logs": [...新增一条...]}。消费端按事件顺序订阅，可用来实时日志/监控。数据量小，默认推荐。
stream_mode="values"：同样在节点执行完成后触发，但事件是“完整状态快照”——当前全量 state（含未改动字段），类似断点快照。直观、便于调试/回放，但体积更大。
执行流程（以 17_graph_stream_support_tutorial.py 为例）：

app 执行 intake → 触发一次 stream 事件（updates: 只含 status/logs 增量；values: 全部 state）。
执行 route → 触发第二个事件。
条件边决定去 analysis_plan 或 fast_answer → 触发第三个事件。
执行 finalize → 触发最后一个事件并结束。
也就是说：流式事件在“节点级”产生，并按执行顺序依次推送，不是“先把整张图一层层展开”也不是“token 级别切块”。与 LLM 输出流式的区别：

流的是“执行事件”，不是文本分片。
事件内容取决于 stream_mode：增量 vs 全量快照。

LLM 流式是“单个节点内部的生成 token 流”，粒度是 token/文本块。
LangGraph 的 stream 是“图级执行事件流”，粒度是节点完成/状态变更。你可以把两者叠加使用：节点内部的 LLM 用 token 流式，节点外层的图用事件流式。
"""

from __future__ import annotations

from copy import deepcopy
from pprint import pformat
import traceback
from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, START, StateGraph


LINE = "=" * 80
SUB_LINE = "-" * 80


def print_section(title: str) -> None:
    """打印章节标题。"""
    print("\n" + LINE)
    print(title)
    print(LINE)


def print_subsection(title: str) -> None:
    """打印小节标题。"""
    print("\n" + SUB_LINE)
    print(title)
    print(SUB_LINE)


def print_state(title: str, state: Dict[str, Any]) -> None:
    """格式化打印状态。"""
    print(f"{title}:\n{pformat(state, width=100, sort_dicts=False)}")


def print_key_points(points: List[str]) -> None:
    """打印关键点总结。"""
    print("\n关键点总结：")
    for idx, point in enumerate(points, start=1):
        print(f"  {idx}. {point}")


def mask_text(text: str) -> str:
    """
    简单脱敏函数（教学版）：
    - 长文本只保留前后片段，避免日志泄漏完整用户输入。
    """
    if len(text) <= 12:
        return text
    return f"{text[:6]}...{text[-4:]}"


def mask_event(event: Any) -> Any:
    """递归脱敏事件对象中的 user_query 字段。"""
    if isinstance(event, dict):
        masked: Dict[str, Any] = {}
        for key, value in event.items():
            if key == "user_query" and isinstance(value, str):
                masked[key] = mask_text(value)
            else:
                masked[key] = mask_event(value)
        return masked
    if isinstance(event, list):
        return [mask_event(item) for item in event]
    return event


# ==================== 1) 定义状态与节点 ====================

class StreamTutorialState(TypedDict):
    """教程图状态"""

    request_id: str
    user_query: str
    route: str
    plan: List[str]
    result: str
    status: str
    logs: List[str]
    score: float


def node_intake(state: StreamTutorialState) -> Dict[str, Any]:
    """入口节点：记录请求并设置处理中状态。"""
    print_subsection("【节点】intake：接收请求")
    query = state["user_query"]
    print(f"接收到 user_query: {query}")

    logs = list(state.get("logs", []))
    logs.append("intake: request accepted")
    return {"status": "processing", "logs": logs}


def node_route(state: StreamTutorialState) -> Dict[str, Any]:
    """路由节点：按查询内容选择后续分支。"""
    print_subsection("【节点】route：意图路由")
    query = state["user_query"]
    route = "analysis" if ("分析" in query or "策略" in query) else "fast"
    print(f"路由决策 route = {route}")

    logs = list(state.get("logs", []))
    logs.append(f"route: choose {route}")
    return {"route": route, "logs": logs}


def node_analysis_plan(state: StreamTutorialState) -> Dict[str, Any]:
    """分析分支：输出更结构化的计划。"""
    print_subsection("【节点】analysis_plan：生成分析计划")
    plan = [
        "拆解业务目标与约束",
        "识别可观测指标与风险",
        "形成可执行的分阶段方案",
    ]
    result = "已进入分析路径：输出结构化方案草稿。"

    logs = list(state.get("logs", []))
    logs.append("analysis_plan: plan generated")
    return {"plan": plan, "result": result, "logs": logs}


def node_fast_answer(state: StreamTutorialState) -> Dict[str, Any]:
    """快速分支：输出简版结论。"""
    print_subsection("【节点】fast_answer：生成快速结果")
    result = "已进入快速路径：输出简要结论。"
    logs = list(state.get("logs", []))
    logs.append("fast_answer: quick result generated")
    return {"result": result, "logs": logs}


def node_finalize(state: StreamTutorialState) -> Dict[str, Any]:
    """收尾节点：统一落地状态并打分。"""
    print_subsection("【节点】finalize：收尾")
    score = 0.92 if state.get("route") == "analysis" else 0.82
    logs = list(state.get("logs", []))
    logs.append("finalize: state completed")
    return {"status": "done", "score": score, "logs": logs}


def route_to_next(state: StreamTutorialState) -> str:
    """条件边：将请求路由到不同节点。"""
    return "analysis_plan" if state.get("route") == "analysis" else "fast_answer"


def build_stream_tutorial_graph():
    """构建并编译教程图。"""
    graph = StateGraph(StreamTutorialState)
    graph.add_node("intake", node_intake)
    graph.add_node("route", node_route)
    graph.add_node("analysis_plan", node_analysis_plan)
    graph.add_node("fast_answer", node_fast_answer)
    graph.add_node("finalize", node_finalize)

    graph.add_edge(START, "intake")
    graph.add_edge("intake", "route")
    graph.add_conditional_edges(
        "route",
        route_to_next,
        {"analysis_plan": "analysis_plan", "fast_answer": "fast_answer"},
    )
    graph.add_edge("analysis_plan", "finalize")
    graph.add_edge("fast_answer", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


def make_initial_state(query: str, request_id: str) -> StreamTutorialState:
    """生成初始状态，避免示例间状态污染。"""
    return {
        "request_id": request_id,
        "user_query": query,
        "route": "",
        "plan": [],
        "result": "",
        "status": "new",
        "logs": [],
        "score": 0.0,
    }


# ==================== 2) 示例一：invoke vs stream ====================

def example_1_invoke_vs_stream() -> None:
    """示例 1：对比一次性返回和增量返回。"""
    print_section("示例 1：invoke 与 stream 的行为差异")
    app = build_stream_tutorial_graph()
    initial = make_initial_state("请给我一个企业运营策略分析框架", "REQ-STREAM-001")

    print_state("初始状态", initial)

    print_subsection("1) invoke：等待图执行完成后一次性拿到最终状态")
    invoke_result = app.invoke(deepcopy(initial))
    print_state("invoke 最终结果", invoke_result)

    print_subsection("2) stream(updates)：节点执行时持续输出增量")
    for idx, event in enumerate(app.stream(deepcopy(initial), stream_mode="updates"), start=1):
        print(f"[stream-updates] 事件#{idx}")
        print(pformat(event, width=100, sort_dicts=False))

    print("\n限制：只用 invoke，线上排障时看不到中间过程。")
    print("解决方案：在生产链路接入 stream(updates) 做实时可观测。")
    print_key_points(
        [
            "invoke 适合只关心最终结果的场景。",
            "stream 适合调试、审计、实时展示和长流程反馈。",
            "两者可以并存：业务用 invoke，平台层用 stream 观测。",
        ]
    )


# ==================== 3) 示例二：updates 模式（推荐默认） ====================

def example_2_stream_mode_updates() -> None:
    """示例 2：演示 updates 模式更轻量。"""
    print_section("示例 2：stream_mode='updates'（企业默认推荐）")
    app = build_stream_tutorial_graph()
    initial = make_initial_state("请快速给出一个日报模板", "REQ-STREAM-002")

    print_state("初始状态", initial)
    audit_rows: List[Dict[str, Any]] = []

    for idx, event in enumerate(app.stream(deepcopy(initial), stream_mode="updates"), start=1):
        row = {
            "event_index": idx,
            "request_id": initial["request_id"],
            "mode": "updates",
            "event": event,
        }
        audit_rows.append(row)
        print(f"[updates] 事件#{idx} -> {pformat(event, width=100, sort_dicts=False)}")

    print_subsection("审计结果（节选）")
    for row in audit_rows[:3]:
        print(pformat(row, width=100, sort_dicts=False))

    print("\n限制：下游如果强依赖“事件字典的内部结构”，升级后可能脆弱。")
    print("解决方案：定义平台层标准事件格式，业务方只消费标准格式。")
    print_key_points(
        [
            "updates 只推送增量，日志量和网络负担更可控。",
            "适合作为线上默认流式观测通道。",
            "建议加一层标准化转换，避免业务代码直接耦合底层细节。",
        ]
    )


# ==================== 4) 示例三：values 模式（完整快照） ====================

def example_3_stream_mode_values() -> None:
    """示例 3：演示 values 模式返回完整状态快照。"""
    print_section("示例 3：stream_mode='values'（完整状态快照）")
    app = build_stream_tutorial_graph()
    initial = make_initial_state("请分析下季度销售增长策略", "REQ-STREAM-003")

    print_state("初始状态", initial)
    snapshots: List[Dict[str, Any]] = []

    for idx, snapshot in enumerate(app.stream(deepcopy(initial), stream_mode="values"), start=1):
        snapshots.append(snapshot)
        light_view = {
            "status": snapshot.get("status"),
            "route": snapshot.get("route"),
            "result": snapshot.get("result"),
            "score": snapshot.get("score"),
            "logs_count": len(snapshot.get("logs", [])),
        }
        print(f"[values] 快照#{idx} -> {light_view}")

    print_subsection("最终快照")
    if snapshots:
        print_state("last snapshot", snapshots[-1])

    print("\n限制：values 每次都传完整状态，状态大时成本会升高。")
    print("解决方案：线上默认 updates；只在调试/回放场景切到 values。")
    print_key_points(
        [
            "values 直观，适合教学、调试和状态回放。",
            "updates 更轻，适合常态化生产监控。",
            "模式选择是成本与可读性的平衡问题。",
        ]
    )


# ==================== 5) 示例四：企业级流式消费封装 ====================

def consume_stream_with_audit(app: Any, state: StreamTutorialState) -> List[Dict[str, Any]]:
    """
    企业封装示例：
    1. 统一事件结构
    2. 对敏感字段做脱敏
    3. 记录失败位置，便于回放
    """
    records: List[Dict[str, Any]] = []
    try:
        for idx, event in enumerate(app.stream(deepcopy(state), stream_mode="updates"), start=1):
            records.append(
                {
                    "event_index": idx,
                    "request_id": state["request_id"],
                    "stream_mode": "updates",
                    "event": mask_event(event),
                    "status": "ok",
                }
            )
    except Exception as exc:  # pragma: no cover - 教学脚本保留通用容错
        records.append(
            {
                "event_index": len(records) + 1,
                "request_id": state["request_id"],
                "stream_mode": "updates",
                "event": {"error": str(exc)},
                "status": "failed",
            }
        )
    return records


def example_4_enterprise_stream_wrapper() -> None:
    """示例 4：演示企业规范下的 stream 消费层。"""
    print_section("示例 4：企业级 Stream 消费封装（审计 + 脱敏 + 容错）")
    app = build_stream_tutorial_graph()
    initial = make_initial_state(
        "请输出给CEO看的经营分析和组织协同建议，附执行节奏",
        "REQ-STREAM-004",
    )
    print_state("初始状态", initial)

    records = consume_stream_with_audit(app, initial)
    print_subsection("标准化审计事件")
    for row in records:
        print(pformat(row, width=100, sort_dicts=False))

    print("\n限制：直接把底层 stream 事件暴露给业务系统，长期维护成本高。")
    print("解决方案：统一封装消费层，平台治理一次，业务复用多次。")
    print_key_points(
        [
            "统一事件结构是企业级治理的基础。",
            "脱敏要放在平台层，不能依赖业务方自觉处理。",
            "流式封装应该具备失败记录能力，支撑排障与审计。",
        ]
    )


# ==================== 6) 主函数入口 ====================

def main() -> None:
    """按教学顺序执行全部示例。"""
    print("\n" + LINE)
    print("LangGraph 图的 Stream 支持教学脚本启动")
    print("执行顺序：示例1 -> 示例2 -> 示例3 -> 示例4")
    print(LINE)

    example_1_invoke_vs_stream()
    example_2_stream_mode_updates()
    example_3_stream_mode_values()
    example_4_enterprise_stream_wrapper()

    print("\n" + LINE)
    print("教程完成：你可以把 consume_stream_with_audit 复用到真实业务图中。")
    print(LINE)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\n" + LINE)
        print("脚本执行失败")
        print(f"异常类型: {type(exc).__name__}")
        print(f"异常信息: {exc}")
        print("完整 traceback 如下：")
        traceback.print_exc()
        print(LINE)
