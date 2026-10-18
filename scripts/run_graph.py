import uuid

from app.graph import compiled_graph


def main():
    order = {
        "product_id": "wedding_invitation",
        "quantity": 20,
    }

    initial_state = {
        "order_details": order,
        "missing_fields": [],
        "errors": [],
        "trace": [],
    }

    result = compiled_graph.invoke(
        initial_state,
        config={"configurable": {"thread_id": str(uuid.uuid4())}},
    )

    print("\n--- Workflow Result ---")
    print("Order details:", result.get("order_details"))
    print("Missing fields:", result.get("missing_fields"))
    print("Errors:", result.get("errors"))
    print("Quotation:", result.get("quote", {}))

    print("\n--- Execution Trace ---")
    for step in result.get("trace", []):
        print(f"\nNode: {step['node']}")
        print(f"Status: {step['status']}")
        print("Details:", step["details"])


if __name__ == "__main__":
    main()
