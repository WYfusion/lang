"""
LangGraph 子图（Subgraph）教学脚本

主题：
1. 一个 Graph 可以独立运行。
2. 编译后的 Graph 可以作为另一个 Graph 的节点（即子图）。
3. 子图让流程复用更简单，特别适合构建复杂工作流与多 Agent 协作链路。

核心讲解点：
1. 子图的定义与价值：把可复用流程封装成独立图。
2. 子图嵌入：父图通过 `add_node("xxx", compiled_subgraph)` 挂载子图。
3. 状态设计：父图状态需要覆盖子图读写的关键字段。
4. 多阶段复用：同一个子图可以在父图中多次复用，分别承担不同阶段任务。
"""

from __future__ import annotations

from copy import deepcopy
from pprint import pformat
import traceback
from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, START, StateGraph


LINE = "=" * 78
SUB_LINE = "-" * 78


def print_section(title: str) -> None:
    """打印大章节标题。"""
    print("\n" + LINE)
    print(title)
    print(LINE)


def print_subsection(title: str) -> None:
    """打印子章节标题。"""
    print("\n" + SUB_LINE)
    print(title)
    print(SUB_LINE)


def print_state(title: str, state: Dict[str, Any]) -> None:
    """格式化打印状态。"""
    print(f"{title}:\n{pformat(state, width=100, sort_dicts=False)}")


def print_key_points(points: List[str]) -> None:
    """打印关键点总结。"""
    print("\n关键点总结：")
    for index, point in enumerate(points, start=1):
        print(f"  {index}. {point}")


# ==================== 1) 子图状态与节点 ====================

class AnalysisSubgraphState(TypedDict):
    """子图状态：专注“分析目标 -> 提炼事实 -> 评估可信度”"""

    objective: str
    findings: List[str]
    confidence: float


def subgraph_collect_facts(state: AnalysisSubgraphState) -> Dict[str, Any]:
    """子图节点 1：根据 objective 产出结构化要点。"""
    print_subsection("【子图节点】collect_facts：收集事实")
    objective = state["objective"]
    print(f"输入 objective: {objective}")

    findings = [
        f"事实1：'{objective}' 可以被拆成更小的可复用步骤。",
        "事实2：子图的接口是“状态输入 -> 状态输出”，非常适合模块化。",
        "事实3：在多 Agent 场景中，子图天然适合封装某个 Agent 的专职流程。",
    ]

    print("输出 findings（模拟知识提炼结果）：")
    for item in findings:
        print(f"  - {item}")
    return {"findings": findings}


def subgraph_evaluate_confidence(state: AnalysisSubgraphState) -> Dict[str, Any]:
    """子图节点 2：对结果做简单质量评估。"""
    print_subsection("【子图节点】evaluate_confidence：评估可信度")
    findings_count = len(state.get("findings", []))
    confidence = min(0.95, 0.55 + findings_count * 0.10)
    confidence = round(confidence, 2)
    print(f"当前 findings 数量: {findings_count}")
    print(f"估算 confidence: {confidence}")

    if confidence < 0.75:
        print("限制：信息覆盖还不够全面。")
        print("解决方案：增加一轮子图节点或引入外部检索节点。")
    else:
        print("结果：当前可信度达到教学示例要求。")

    return {"confidence": confidence}


def subgraph_quality_gate(state: AnalysisSubgraphState) -> Dict[str, Any]:
    """子图节点 3：质量门禁与补充。"""
    print_subsection("【子图节点】quality_gate：质量门禁")
    confidence = state.get("confidence", 0.0)
    findings = list(state.get("findings", []))

    if confidence < 0.80:
        print("检测到 confidence < 0.80，追加一条补充说明。")
        findings.append("补充事实：子图可以通过版本化维护，降低复杂项目的维护成本。")
        confidence = round(min(0.95, confidence + 0.10), 2)
        print(f"修正后 confidence: {confidence}")
        return {"findings": findings, "confidence": confidence}

    print("quality_gate 通过，无需补充。")
    return {}


def build_analysis_subgraph():
    """构建“分析子图”，可独立运行，也可嵌入父图。"""
    graph = StateGraph(AnalysisSubgraphState)
    graph.add_node("collect_facts", subgraph_collect_facts)
    graph.add_node("evaluate_confidence", subgraph_evaluate_confidence)
    graph.add_node("quality_gate", subgraph_quality_gate)
    graph.add_edge(START, "collect_facts")
    graph.add_edge("collect_facts", "evaluate_confidence")
    graph.add_edge("evaluate_confidence", "quality_gate")
    graph.add_edge("quality_gate", END)
    return graph.compile()


# ==================== 2) 示例一：子图独立运行 ====================

def example_1_subgraph_standalone() -> None:
    """示例 1：先把子图当作普通图单独运行。"""
    print_section("示例 1：子图独立运行（先当普通 Graph 用）")
    subgraph = build_analysis_subgraph()
    initial_state: AnalysisSubgraphState = {
        "objective": "解释 LangGraph 子图是什么，以及为什么可以复用",
        "findings": [],
        "confidence": 0.0,
    }

    print_state("初始状态", initial_state)
    result = subgraph.invoke(initial_state)
    print_state("执行后状态", result)
    print_key_points(
        [
            "子图本质上先是一个可独立执行的图。",
            "子图输出是标准状态字典，后续可以被父图直接消费。",
            "先单测子图，再集成到父图，是更稳的工程实践。",
        ]
    )


# ==================== 3) 示例二：子图作为父图节点 ====================

class ParentState(TypedDict):
    """父图状态：包含用户问题 + **子图需要的字段**(关键，不然无法在父图和子图间通信) + 最终答案。"""

    user_question: str
    objective: str
    findings: List[str]
    confidence: float
    final_answer: str


def parent_prepare_objective(state: ParentState) -> Dict[str, Any]:
    """父图节点 1：把用户问题转为子图 objective。"""
    print_subsection("【父图节点】prepare_objective：准备子图输入")
    user_question = state["user_question"]
    objective = (
        f"围绕问题“{user_question}”提炼三点：定义、复用价值、多 Agent 适用性。"
    )
    print(f"用户问题: {user_question}")
    print(f"生成 objective: {objective}")
    return {"objective": objective, "findings": [], "confidence": 0.0}


def parent_generate_answer(state: ParentState) -> Dict[str, Any]:
    """父图节点 2：根据子图输出生成最终答案。"""
    print_subsection("【父图节点】generate_answer：整合子图结果")
    findings = state.get("findings", [])
    confidence = state.get("confidence", 0.0)

    answer_lines = [
        "结论：在 LangGraph 中，子图是“可复用流程单元”。",
        "说明：一个 Graph 编译后可作为父图节点，从而实现流程嵌套。",
        "价值：可维护、可测试、可组合，尤其适合多 Agent 架构。",
        f"当前示例 confidence: {confidence}",
        "子图提炼要点：",
    ]
    answer_lines.extend([f"- {item}" for item in findings])
    final_answer = "\n".join(answer_lines)

    print("已生成最终答案（节选）：")
    print("\n".join(answer_lines[:4]))
    return {"final_answer": final_answer}


def build_parent_graph_with_subgraph():
    """构建父图：把子图直接挂成一个节点。"""
    # 将示例1中用到的子图编译后作为父图节点使用，核心就是这一步！
    analysis_subgraph = build_analysis_subgraph()   

    graph = StateGraph(ParentState)
    graph.add_node("prepare_objective", parent_prepare_objective)
    graph.add_node("analysis_subgraph", analysis_subgraph)
    graph.add_node("generate_answer", parent_generate_answer)

    graph.add_edge(START, "prepare_objective")
    graph.add_edge("prepare_objective", "analysis_subgraph")
    graph.add_edge("analysis_subgraph", "generate_answer")
    graph.add_edge("generate_answer", END)
    return graph.compile()


def example_2_subgraph_as_node() -> None:
    """示例 2：把子图作为父图节点运行。"""
    print_section("示例 2：子图作为父图节点（核心用法）")
    app = build_parent_graph_with_subgraph()

    initial_state: ParentState = {
        "user_question": "什么是 LangGraph 子图？为什么它对复杂工作流很有用？",
        "objective": "",
        "findings": [],
        "confidence": 0.0,
        "final_answer": "",
    }

    print_state("初始状态", initial_state)
    result = app.invoke(initial_state)
    print_state("执行后状态", result)
    print_key_points(
        [
            "父图与子图通过共享状态字段进行通信。",
            "关键动作是：graph.compile() 后，将其 add_node 到父图。",
            "当流程越来越复杂时，子图是控制复杂度的核心手段。",
        ]
    )


# ==================== 4) 示例三：同一子图复用两次（模拟多 Agent 分工） ====================

class ReuseState(TypedDict):
    """复用场景状态：同一子图执行两个阶段任务。"""

    topic: str
    objective: str
    findings: List[str]
    confidence: float
    iteration_outputs: List[Dict[str, Any]]
    final_strategy: str


def reuse_prepare_round_1(state: ReuseState) -> Dict[str, Any]:
    """回合 1：规划视角。"""
    print_subsection("【父图节点】prepare_round_1：规划 Agent 视角")
    topic = state["topic"]
    objective = f"以规划者视角分析主题“{topic}”的流程拆分方式。"
    print(f"设置 objective: {objective}")
    return {"objective": objective, "findings": [], "confidence": 0.0, "iteration_outputs": []}


def reuse_archive_and_prepare_round_2(state: ReuseState) -> Dict[str, Any]:
    """回合切换：归档回合 1 结果，并准备回合 2 目标。"""
    print_subsection("【父图节点】prepare_round_2：切换执行 Agent 视角")
    outputs = list(state.get("iteration_outputs", []))
    outputs.append(
        {
            "round": "round_1_planner",
            "objective": state.get("objective", ""),
            "findings": deepcopy(state.get("findings", [])),
            "confidence": state.get("confidence", 0.0),
        }
    )
    print("已归档 round_1 结果。")

    topic = state["topic"]
    objective = f"以执行者视角分析主题“{topic}”的落地动作与风险控制。"
    print(f"设置新的 objective: {objective}")
    print("限制：如果不用子图复用，就需要重复写一套几乎相同的节点逻辑。")
    print("解决方案：同一个子图对象在父图中多次挂载，分别承担不同阶段。")
    return {"iteration_outputs": outputs, "objective": objective, "findings": [], "confidence": 0.0}


def reuse_merge_strategy(state: ReuseState) -> Dict[str, Any]:
    """合并两轮结果，输出最终策略。"""
    print_subsection("【父图节点】merge_strategy：整合多轮子图结果")
    outputs = list(state.get("iteration_outputs", []))
    outputs.append(
        {
            "round": "round_2_executor",
            "objective": state.get("objective", ""),
            "findings": deepcopy(state.get("findings", [])),
            "confidence": state.get("confidence", 0.0),
        }
    )

    planner = outputs[0] if outputs else {}
    executor = outputs[1] if len(outputs) > 1 else {}

    final_strategy = "\n".join(
        [
            f"主题：{state['topic']}",
            "阶段 1（规划）建议：",
            f"  - 目标: {planner.get('objective', 'N/A')}",
            f"  - 置信度: {planner.get('confidence', 'N/A')}",
            "阶段 2（执行）建议：",
            f"  - 目标: {executor.get('objective', 'N/A')}",
            f"  - 置信度: {executor.get('confidence', 'N/A')}",
            "总结：同一子图复用两次，形成了简化版多 Agent 串联工作流。",
        ]
    )

    print("已完成策略整合。")
    return {"iteration_outputs": outputs, "final_strategy": final_strategy}


def build_reuse_graph():
    """构建复用图：同一个子图在两个阶段重复使用。"""
    analysis_subgraph = build_analysis_subgraph()

    graph = StateGraph(ReuseState)
    graph.add_node("prepare_round_1", reuse_prepare_round_1)    
    # "iteration_outputs" 是用来在两轮子图之间传递信息的共享字段,
    # 子图 analysis_subgraph 中没有 "iteration_outputs" 很正常，
    # "iteration_outputs"是存储到父图状态中的字段，这里也强烈体现了状态是图的状态，不是节点的状态！！！
    # 子图只需要关注它自己的输入输出字段（objective、findings、confidence）。
    # 父图节点 "prepare_round_2" 负责把第一轮子图的结果归档到"iteration_outputs"里，
    # 然后设置新的objective供第二轮子图使用。这样就实现了两轮子图通过父图状态进行信息传递和复用，
    # 而不需要在子图里直接处理"iteration_outputs"字段。
    graph.add_node("analysis_round_1", analysis_subgraph)
    graph.add_node("prepare_round_2", reuse_archive_and_prepare_round_2)
    graph.add_node("analysis_round_2", analysis_subgraph)
    graph.add_node("merge_strategy", reuse_merge_strategy)

    graph.add_edge(START, "prepare_round_1")
    graph.add_edge("prepare_round_1", "analysis_round_1")
    graph.add_edge("analysis_round_1", "prepare_round_2")
    graph.add_edge("prepare_round_2", "analysis_round_2")
    graph.add_edge("analysis_round_2", "merge_strategy")
    graph.add_edge("merge_strategy", END)
    return graph.compile()


def example_3_reuse_subgraph_for_multi_agent_style() -> None:
    """示例 3：同一子图复用两次，模拟多 Agent 分工。"""
    print_section("示例 3：复用同一子图两次（模拟多 Agent 分工）")
    app = build_reuse_graph()

    initial_state: ReuseState = {
        "topic": "构建可维护的 LangGraph 多 Agent 工作流",
        "objective": "",
        "findings": [],
        "confidence": 0.0,
        "iteration_outputs": [],
        "final_strategy": "",
    }

    print_state("初始状态", initial_state)
    result = app.invoke(initial_state)
    print_state("执行后状态", result)
    print("\n最终策略：")
    print(result.get("final_strategy", "N/A"))
    print_key_points(
        [
            "复用不是“复制粘贴节点”，而是“复用子图能力”。",
            "同一个子图可挂在父图多个位置，承担不同阶段职责。",
            "这就是子图在复杂编排和多 Agent 系统中的工程价值。",
        ]
    )


# ==================== 5) 示例四：适配层隔离（子图私有键） ====================

class PrivateAnalysisState(TypedDict):
    """子图私有状态：这组键不会暴露给父图。"""

    private_objective: str
    private_findings: List[str]
    private_confidence: float
    internal_trace: List[str]


def private_collect(state: PrivateAnalysisState) -> Dict[str, Any]:
    """私有子图节点 1：使用私有键完成采集。"""
    print_subsection("【私有子图节点】private_collect：仅操作私有键")
    objective = state["private_objective"]
    findings = [
        f"私有事实1：目标“{objective}”先分层再拆任务。",
        "私有事实2：对子图内部细节做封装，父图不需要感知。",
        "私有事实3：适配层负责输入输出映射，避免状态键污染。",
    ]
    trace = list(state.get("internal_trace", []))
    trace.append("private_collect_done")
    return {"private_findings": findings, "internal_trace": trace}


def private_score(state: PrivateAnalysisState) -> Dict[str, Any]:
    """私有子图节点 2：输出私有置信度。"""
    print_subsection("【私有子图节点】private_score：计算私有置信度")
    score = round(min(0.96, 0.60 + 0.10 * len(state.get("private_findings", []))), 2)
    trace = list(state.get("internal_trace", []))
    trace.append("private_score_done")
    print(f"私有评分 private_confidence: {score}")
    return {"private_confidence": score, "internal_trace": trace}


def build_private_analysis_subgraph():
    """构建私有子图：状态键与父图完全不同。"""
    graph = StateGraph(PrivateAnalysisState)
    graph.add_node("private_collect", private_collect)
    graph.add_node("private_score", private_score)
    graph.add_edge(START, "private_collect")
    graph.add_edge("private_collect", "private_score")
    graph.add_edge("private_score", END)
    return graph.compile()


class AdapterParentState(TypedDict):
    """父图状态：只保留业务共享键，不暴露子图私有键。"""

    user_question: str
    objective: str
    findings: List[str]
    confidence: float
    final_answer: str


def adapter_prepare_objective(state: AdapterParentState) -> Dict[str, Any]:
    """父图节点：准备共享输入。"""
    print_subsection("【父图节点】adapter_prepare_objective：准备共享输入")
    question = state["user_question"]
    objective = f"请针对“{question}”给出可复用工作流的关键原则。"
    print(f"父图生成 objective: {objective}")
    return {"objective": objective, "findings": [], "confidence": 0.0}


def adapter_run_private_subgraph(state: AdapterParentState) -> Dict[str, Any]:
    """适配层：把父图共享键映射到子图私有键，再映射回父图。"""
    print_subsection("【适配层】adapter_run_private_subgraph：输入输出映射")
    private_subgraph = build_private_analysis_subgraph()

    # Step 1: 输入映射（父图 -> 私有子图）
    private_input: PrivateAnalysisState = {
        "private_objective": state["objective"],
        "private_findings": [],
        "private_confidence": 0.0,
        "internal_trace": [],
    }
    print("输入映射：objective -> private_objective")

    private_result = private_subgraph.invoke(private_input)
    print_state("私有子图执行后状态（仅教学展示）", private_result)

    # Step 2: 输出映射（私有子图 -> 父图）
    mapped_findings = list(private_result.get("private_findings", []))
    mapped_confidence = float(private_result.get("private_confidence", 0.0))
    print("输出映射：private_findings -> findings, private_confidence -> confidence")
    return {"findings": mapped_findings, "confidence": mapped_confidence}


def build_adapter_layer_graph():
    """构建父图：通过适配层调用私有子图，实现状态隔离。"""
    graph = StateGraph(AdapterParentState)
    graph.add_node("prepare_objective", adapter_prepare_objective)
    graph.add_node("adapt_and_run_private_subgraph", adapter_run_private_subgraph)
    graph.add_node("generate_answer", parent_generate_answer)

    graph.add_edge(START, "prepare_objective")
    graph.add_edge("prepare_objective", "adapt_and_run_private_subgraph")
    graph.add_edge("adapt_and_run_private_subgraph", "generate_answer")
    graph.add_edge("generate_answer", END)
    return graph.compile()


def example_4_adapter_layer_isolation() -> None:
    """示例 4：适配层隔离，演示子图私有键不暴露给父图。"""
    print_section("示例 4：适配层隔离（子图私有键与父图共享键分离）")
    app = build_adapter_layer_graph()

    initial_state: AdapterParentState = {
        "user_question": "如何在复杂系统里复用子流程，又不污染全局状态键？",
        "objective": "",
        "findings": [],
        "confidence": 0.0,
        "final_answer": "",
    }

    print_state("初始父图状态", initial_state)
    result = app.invoke(initial_state)
    print_state("执行后父图状态", result)
    print_key_points(
        [
            "适配层隔离 = 输入映射 + 私有子图执行 + 输出映射。",
            "父图无需包含 private_* 键，也能消费子图能力。",
            "这是一种避免状态命名冲突、提升可维护性的常见工程手段。",
        ]
    )


# ==================== 6) 主函数入口 ====================

def main() -> None:
    """按教学顺序运行全部示例。"""
    print("\n" + LINE)
    print("LangGraph 子图教学脚本启动")
    print("运行顺序：示例1（独立运行） -> 示例2（嵌入父图） -> 示例3（复用多阶段） -> 示例4（适配层隔离）")
    print(LINE)

    example_1_subgraph_standalone()
    example_2_subgraph_as_node()
    example_3_reuse_subgraph_for_multi_agent_style()
    example_4_adapter_layer_isolation()

    print("\n" + LINE)
    print("脚本运行完成：你可以把“分析子图”替换成任意业务子流程，然后复用到更大父图中。")
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
