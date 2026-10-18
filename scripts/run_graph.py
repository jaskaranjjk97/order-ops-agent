from uuid import uuid4

from app.graph import compiled_graph


def main():
    initial_state = {
        "customer_message": "I need 100 wedding invitations printed.",
        "trace": [],
    }

    result = compiled_graph.invoke(
        initial_state,
        config={
            "configurable": {
                "thread_id": str(uuid4()),
            }
        },
    )

    print("\n--- Workflow Result ---")
    print("Customer message:", result.get("customer_message"))
    print("Order details:", result.get("order_details"))
    print("Missing fields:", result.get("missing_fields", []))
    print("Errors:", result.get("errors", []))
    print("Quotation:", result.get("quote", {}))

    print("\n--- Execution Trace ---")
    for step in result.get("trace", []):
        print(f"\nNode: {step['node']}")
        print(f"Status: {step['status']}")
        print("Details:", step["details"])


if __name__ == "__main__":
    main()
