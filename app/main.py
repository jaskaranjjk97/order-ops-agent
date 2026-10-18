import uuid

from fastapi import FastAPI
from langgraph.types import Command
from pydantic import BaseModel, Field

from app.graph import compiled_graph

app = FastAPI(
    title="OrderOps Agent API",
    description="API for order extraction, validation, quotation, and approval.",
    version="1.0.0",
)


class OrderRequest(BaseModel):
    customer_message: str = Field(min_length=1)


class ApprovalRequest(BaseModel):
    approved: bool


@app.get("/health")
def health():
    """check whether api is running properly."""
    return {
        "status": "ok",
    }


@app.post("/api/v1/orders")
def create_order(request: OrderRequest):
    """Extract, validate, quote, and request approval for an order."""
    thread_id = str(uuid.uuid4())

    result = compiled_graph.invoke(
        {"customer_message": request.customer_message, "trace": []},
        config={"configurable": {"thread_id": thread_id}},
    )

    interrupt = result.get("__interrupt__", [])

    if interrupt:
        approval_data = interrupt[0].value

        return {
            "status": "pending_approval",
            "thread_id": thread_id,
            "order_details": approval_data["order_details"],
            "quote": approval_data["quote"],
            "trace": result.get("trace", []),
        }
    if result.get("errors"):
        status = "invalid"
    elif result.get("missing_fields"):
        status = "needs_input"
    else:
        status = "completed"

    return {
        "status": status,
        "thread_id": thread_id,
        "order_details": result.get("order_details", {}),
        "missing_fields": result.get("missing_fields", []),
        "errors": result.get("errors", []),
        "quote": result.get("quote", {}),
        "trace": result.get("trace", []),
    }


@app.post("/api/v1/orders/{thread_id}/approval")
def approve_order(thread_id: str, request: ApprovalRequest):
    """Resume a paused order workflow with the human's decision."""

    result = compiled_graph.invoke(
        Command(resume={"approved": request.approved}),
        config={"configurable": {"thread_id": thread_id}},
    )

    return {
        "status": result.get("approval_status", "unknown"),
        "thread_id": thread_id,
        "order_id": result.get("order_id"),
        "quote": result.get("quote", {}),
        "trace": result.get("trace", []),
    }
