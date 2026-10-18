from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from app.nodes.approve import approve_order
from app.nodes.extract import extract_order
from app.nodes.quote import create_quote
from app.nodes.validate import validate_order
from app.state import OrderState


def route_after_validation(state: OrderState) -> str:
    """Route based on the validation results."""

    if state.get("missing_fields") or state.get("errors"):
        return "stop"

    return "quote"


def build_graph():
    graph = StateGraph(OrderState)

    graph.add_node("extract", extract_order)
    graph.add_node("validate", validate_order)
    graph.add_node("quote", create_quote)
    graph.add_node("approve", approve_order)

    graph.add_edge(START, "extract")
    graph.add_edge("extract", "validate")

    graph.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "quote": "quote",
            "stop": END,
        },
    )

    graph.add_edge("quote", "approve")
    graph.add_edge("approve", END)

    return graph.compile(checkpointer=InMemorySaver())


compiled_graph = build_graph()
