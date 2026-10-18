import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="OrderOps Agent",
    page_icon="📦",
    layout="centered",
)

st.title("📦 OrderOps Agent")
st.caption("AI-powered order processing and quotation management")

# Keep the order workflow information between Streamlit reruns.
if "order_result" not in st.session_state:
    st.session_state.order_result = None

if "approval_result" not in st.session_state:
    st.session_state.approval_result = None

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None


st.header("1. Submit an order")

customer_message = st.text_area(
    "Describe the order",
    placeholder="I need 100 wedding invitations printed.",
    height=100,
)

if st.button("Generate quotation", type="primary"):
    if not customer_message.strip():
        st.warning("Please enter an order description.")
    else:
        try:
            response = requests.post(
                f"{API_URL}/api/v1/orders",
                json={"customer_message": customer_message.strip()},
                timeout=120,
            )
            response.raise_for_status()

            result = response.json()

            st.session_state.order_result = result
            st.session_state.approval_result = None
            st.session_state.thread_id = result.get("thread_id")

        except requests.RequestException as exc:
            st.error(f"Could not connect to the API: {exc}")


result = st.session_state.order_result

if result:
    status = result.get("status")

    st.divider()
    st.header("2. Order details")

    st.write("**Status:**", status)

    st.json(result.get("order_details", {}))

    if result.get("missing_fields"):
        st.warning(
            "More information is required: " + ", ".join(result["missing_fields"])
        )

    if result.get("errors"):
        for error in result["errors"]:
            st.error(error)

    quote = result.get("quote", {})

    if quote:
        st.subheader("Quotation")

        col1, col2 = st.columns(2)

        col1.metric("Quantity", quote.get("quantity", 0))
        col2.metric(
            "Unit price",
            f"₹{quote.get('unit_price', 0):,.2f}",
        )

        st.metric(
            "Total amount",
            f"₹{quote.get('total', 0):,.2f}",
        )

    # Show approval controls only when approval is pending.
    if status == "pending_approval":
        st.divider()
        st.header("3. Review and approve")

        st.write("Review the quotation before approving or rejecting this order.")

        col1, col2 = st.columns(2)

        with col1:
            approve_clicked = st.button(
                "Approve order",
                type="primary",
            )

        with col2:
            reject_clicked = st.button("Reject order")

        if approve_clicked or reject_clicked:
            try:
                approval_response = requests.post(
                    f"{API_URL}/api/v1/orders/{st.session_state.thread_id}/approval",
                    json={"approved": approve_clicked},
                    timeout=60,
                )
                approval_response.raise_for_status()

                st.session_state.approval_result = approval_response.json()

            except requests.RequestException as exc:
                st.error(f"Approval request failed: {exc}")

    approval = st.session_state.approval_result

    if approval:
        st.divider()
        st.header("Final result")

        if approval.get("status") == "approved":
            st.success("Order approved successfully.")

            st.write("**Order ID:**", approval.get("order_id"))
        elif approval.get("status") == "rejected":
            st.warning("The order was rejected.")
        else:
            st.error(f"Unexpected workflow status: {approval.get('status')}")

    with st.expander("Execution trace"):
        trace = (
            st.session_state.approval_result.get("trace", [])
            if st.session_state.approval_result
            else result.get("trace", [])
        )

        for step in trace:
            st.markdown(f"**{step['node']}** — {step['status']}")
            st.json(step["details"])
