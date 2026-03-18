from langgraph.types import Command
from graph import app


# Initial input to graph
initial_state = {
    "email_content": "How do I reset my password??",
    "sender_email": "Mujahidtes@gmail.com",
    "email_id": "email_1234567",
    "classification": None,
    "search_results": None,
    "customer_history": None,
    "draft_response": None,
    "messages": [],
}

# thread_id is important for durable execution
# It helps LangGraph remember the same workflow state
config = {
    "configurable": {
        "thread_id": "customer-thread-007"
    }
}

print("\n===== FIRST RUN =====")
result = app.invoke(initial_state, config=config)

# If graph pauses at interrupt(), LangGraph returns __interrupt__
if "__interrupt__" in result:
    print("\nGraph paused for human review.")
    print("Interrupt payload:")
    payload = result["__interrupt__"]
    # Safe print for Windows console (cp1252 can't encode e.g. →)
    print(str(payload).encode("ascii", errors="replace").decode("ascii"))

    # Simulate human approval
    human_input = Command(
        resume={
            "approved": True,
            "edited_response": (
                "We sincerely apologize for the double charge. "
                "Our billing team has reviewed your case and initiated the refund. "
                "You will receive confirmation shortly."
            ),
        }
    )

    print("\n===== RESUMING AFTER HUMAN APPROVAL =====")
    final_result = app.invoke(human_input, config=config)
    print("\nWorkflow completed.")