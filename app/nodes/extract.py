import json

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app import config
from app.llm import get_llm
from app.state import OrderState


class ExtractOrder(BaseModel):
    product_id: str | None = Field(
        default=None,
        description="Product ID from the available product catalogue.",
    )
    quantity: int | None = Field(
        default=None,
        description="Requested whole-number quantity, or null if missing or unclear.",
    )


def extract_order(state: OrderState) -> dict:
    """LangGraph Node: extracts product_id and quantity from the customer message."""

    with open(config.PRODUCTS_FILE, encoding="utf-8") as file:
        products = json.load(file)["products"]

    message = state.get("customer_message", "")

    ORDER_SYSTEM = f"""
    Extract order details from the customer message.

Available products:
{json.dumps(products, indent=2)}

Rules:
- Return a product_id only when the requested product matches a product
  in the catalogue. Use its exact product ID.
- Return quantity only when the customer specifies a clear whole number.
- If the product or quantity is missing or unclear, return null for that field.
- Do not invent information or guess missing values.

"""

    llm = get_llm(temperature=0.0).with_structured_output(ExtractOrder)
    results = llm.invoke(
        [
            SystemMessage(content=ORDER_SYSTEM),
            HumanMessage(content=message),
        ]
    )
    order_details = results.model_dump()

    status = (
        "ok"
        if all(value is not None for value in order_details.values())
        else "needs_input"
    )

    return {
        "order_details": order_details,
        "trace": state.get("trace", [])
        + [
            {
                "node": "extract",
                "status": status,
                "details": {
                    "product_id": order_details["product_id"],
                    "quantity": order_details["quantity"],
                },
            }
        ],
    }
