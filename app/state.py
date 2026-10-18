from typing import TypedDict


class OrderState(TypedDict, total=False):
    customer_message: str
    order_details: dict
    missing_fields: list[str]
    errors: list[str]
    quote: dict
    approval_status: str
    order_id: str
    trace: list[dict]
