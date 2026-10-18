import json

from app import config
from app.state import OrderState


def create_quote(state: OrderState) -> dict:
    """Calculate the quotation for a valid order."""

    missing_fields = state.get("missing_fields", [])
    errors = state.get("errors", [])

    if missing_fields or errors:
        reasons = []

        if missing_fields:
            reasons.append(f"Missing fields: {missing_fields}")

        if errors:
            reasons.extend(errors)

        return {
            "quote": {},
            "trace": state.get("trace", [])
            + [
                {
                    "node": "quote",
                    "status": "skipped",
                    "details": {
                        "reason": reasons,
                    },
                }
            ],
        }

    order = state.get("order_details") or {}

    with open(config.PRODUCTS_FILE, encoding="utf-8") as file:
        products = json.load(file)["products"]

    product = products[order["product_id"]]
    quantity = order["quantity"]

    unit_price = product["unit_price"]
    subtotal = round(quantity * unit_price, 2)

    return {
        "quote": {
            "product_id": order["product_id"],
            "product_name": product["name"],
            "quantity": quantity,
            "unit_price": unit_price,
            "subtotal": subtotal,
            "total": subtotal,
            "currency": "INR",
        },
        "trace": state.get("trace", [])
        + [
            {
                "node": "quote",
                "status": "ok",
                "details": {
                    "product_id": order["product_id"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total": subtotal,
                },
            }
        ],
    }
