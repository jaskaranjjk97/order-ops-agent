import json

from app import config
from app.state import OrderState


def validate_order(state: OrderState) -> dict:
    """Validate the order details extracted by the LLM."""

    order = state.get("order_details") or {}
    missing_fields = []
    errors = []

    product_id = order.get("product_id")
    quantity = order.get("quantity")

    if not product_id:
        missing_fields.append("product_id")

    if quantity is None:
        missing_fields.append("quantity")
    elif isinstance(quantity, bool) or not isinstance(quantity, int):
        errors.append("Quantity must be a whole number.")
    elif quantity <= 0:
        errors.append("Quantity must be greater than zero.")

    if product_id:
        with open(config.PRODUCTS_FILE, encoding="utf-8") as file:
            products = json.load(file)["products"]

        if product_id not in products:
            errors.append(f"Unknown product: {product_id}")

        elif (
            isinstance(quantity, int)
            and not isinstance(quantity, bool)
            and quantity > 0
            and quantity < products[product_id]["min_quantity"]
        ):
            errors.append(
                f"Minimum quantity for {product_id} is "
                f"{products[product_id]['min_quantity']}."
            )

    if errors:
        status = "error"
    elif missing_fields:
        status = "needs_input"
    else:
        status = "ok"

    return {
        "missing_fields": missing_fields,
        "errors": errors,
        "trace": state.get("trace", [])
        + [
            {
                "node": "validate",
                "status": status,
                "details": {
                    "product_id": product_id,
                    "quantity": quantity,
                    "missing_fields": missing_fields,
                    "errors": errors,
                },
            }
        ],
    }
