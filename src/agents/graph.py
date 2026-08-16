"""LangGraph StateGraph builder for Enterprise Agentic Hybrid RAG."""

from typing import Literal
from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from src.agents.nodes import AgentNodeRunner
from config.settings import settings


def build_rag_graph(node_runner: AgentNodeRunner | None = None) -> StateGraph:
    """Construct and compile the state machine graph."""
    runner = node_runner or AgentNodeRunner()
    builder = StateGraph(AgentState)

    # 1. Register all State Nodes
    builder.add_node("input_guard", runner.input_guard_node)
    builder.add_node("router", runner.router_node)
    builder.add_node("retrieval", runner.retrieval_node)
    builder.add_node("synthesis", runner.synthesis_node)
    builder.add_node("critic", runner.critic_node)
    builder.add_node("output_guard", runner.output_guard_node)

    # 2. Set Entry Point
    builder.set_entry_point("input_guard")

    # 3. Conditional Edge: Input Guardrail Check
    def check_input_safety(state: AgentState) -> Literal["router", "safe_refusal"]:
        if not state.get("is_safe", True):
            return "safe_refusal"
        return "router"

    builder.add_conditional_edges(
        "input_guard",
        check_input_safety,
        {
            "router": "router",
            "safe_refusal": END,
        }
    )

    # 4. Conditional Edge: Router Decision
    def check_route(state: AgentState) -> Literal["retrieval", "synthesis"]:
        if state.get("route") == "direct":
            return "synthesis"
        return "retrieval"

    builder.add_conditional_edges(
        "router",
        check_route,
        {
            "retrieval": "retrieval",
            "synthesis": "synthesis",
        }
    )

    # 5. Standard Edge: Retrieval -> Synthesis
    builder.add_edge("retrieval", "synthesis")

    # 6. Standard Edge: Synthesis -> Critic
    builder.add_edge("synthesis", "critic")

    # 7. Conditional Edge: Critic Entailment Gate / Self-Correction Loop
    def check_critic_verdict(state: AgentState) -> Literal["output_guard", "refine_retry"]:
        verdict = state.get("critic_verdict", "PASS")
        retry_count = state.get("retry_count", 0)

        # If passed or exceeded max retries, proceed to output guardrail
        if verdict == "PASS" or retry_count > settings.MAX_CRITIC_RETRIES:
            return "output_guard"
        # Otherwise, loop back to router for query refinement with critique
        return "refine_retry"

    builder.add_conditional_edges(
        "critic",
        check_critic_verdict,
        {
            "output_guard": "output_guard",
            "refine_retry": "router",
        }
    )

    # 8. Standard Edge: Output Guard -> END
    builder.add_edge("output_guard", END)

    return builder.compile()
