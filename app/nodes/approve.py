import json
from uuid import uuid4

from langgraph.types import interrupt

from app import config
from app.state import OrderState


def approve_order(state: OrderState) -> dict:
    """Pause for human approval or rejection of an order."""

    human_decision = interrupt(
        {
            "message": "Review this quotation and approve or reject it.",
            "order_details": state.get("order_details", {}),
            "quote": state.get("quote", {}),
        }
    )

    approved = (
        human_decision.get("approved") is True
        if isinstance(human_decision, dict)
        else human_decision is True
    )

    if not approved:
        return {
            "approval_status": "rejected",
            "trace": state.get("trace", [])
            + [
                {
                    "node": "approve",
                    "status": "rejected",
                    "details": {
                        "reason": "Quotation rejected by human reviewer.",
                    },
                }
            ],
        }

    with open(config.ORDERS_FILE, encoding="utf-8") as file:
        data = json.load(file)

    order_id = str(uuid4())

    order_record = {
        "order_id": order_id,
        "order_details": state["order_details"],
        "quote": state["quote"],
        "approval_status": "approved",
    }

    data["existing_orders"].append(order_record)

    with open(config.ORDERS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    return {
        "approval_status": "approved",
        "order_id": order_id,
        "trace": state.get("trace", [])
        + [
            {
                "node": "approve",
                "status": "approved",
                "details": {
                    "order_id": order_id,
                    "total": state["quote"]["total"],
                },
            }
        ],
    }
