from uuid import uuid4

from langgraph.types import Command

from app.graph import compiled_graph


def main():
    initial_state = {
        "customer_message": "I need 100 wedding invitations printed.",
        "trace": [],
    }

    run_config = {
        "configurable": {
            "thread_id": str(uuid4()),
        }
    }

    result = compiled_graph.invoke(initial_state, config=run_config)

    if result.get("__interrupt__"):
        interrupt_data = result["__interrupt__"][0].value

        print("\n--- Approval Required ---")
        print("Order details:", interrupt_data["order_details"])
        print("Quotation:", interrupt_data["quote"])

        decision = input("\nApprove this quotation? (yes/no): ")
        approved = decision.strip().lower() in {"yes", "y"}

        result = compiled_graph.invoke(
            Command(resume={"approved": approved}),
            config=run_config,
        )

    print("\n--- Workflow Result ---")
    print("Order details:", result.get("order_details"))
    print("Missing fields:", result.get("missing_fields", []))
    print("Errors:", result.get("errors", []))
    print("Quotation:", result.get("quote", {}))
    print("Approval status:", result.get("approval_status"))
    print("Order ID:", result.get("order_id"))

    print("\n--- Execution Trace ---")
    for step in result.get("trace", []):
        print(f"\nNode: {step['node']}")
        print(f"Status: {step['status']}")
        print("Details:", step["details"])


if __name__ == "__main__":
    main()
