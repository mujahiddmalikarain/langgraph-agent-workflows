from typing import Literal
from langgraph.types import Command, interrupt
from langchain_openai import ChatOpenAI
from state import EmailAgentState, EmailClassification
from rag.retriver import retrieve_docs

# Create LLM instance
llm = ChatOpenAI(model="gpt-5-nano",verbose=True)



def read_email(state: EmailAgentState) -> dict:
    """
    This node just reads the email from the input state.
    In real production, this could connect to Gmail, Outlook, etc.
    """
    print("\n[Node] read_email")

    return {
        "messages": [f"Email received from {state['sender_email']}"]
    }


def classify_intent(
    state: EmailAgentState,
) -> Command[Literal["search_documentation", "bug_tracking", "human_review", "draft_response"]]:
    """
    This node uses the LLM to classify:
    - intent
    - urgency
    - topic
    - summary

    Then it decides which node should run next.
    """
    print("\n[Node] classify_intent")

    structured_llm = llm.with_structured_output(EmailClassification)

    prompt = f"""
    Classify this customer support email.

    Email:
    {state['email_content']}

    Return:
    - intent: question, bug, billing, feature, complex
    - urgency: low, medium, high, critical
    - topic
    - summary
    """

    classification = structured_llm.invoke(prompt)

    print("Classification:", classification)

    # Routing logic
    if classification["intent"] == "bug":
        goto = "bug_tracking"
    elif classification["intent"] in ["question", "feature"]:
        goto = "search_documentation"
    elif classification["intent"] == "billing" or classification["urgency"] == "critical":
        goto = "human_review"
    else:
        goto = "draft_response"

    return Command(
        update={"classification": classification},
        goto=goto,
    )



def search_documentation(state):
    print("\n[Node] search_documentation")
    query = state["email_content"]
    docs = retrieve_docs(query)
    return {"search_results": docs}
     


def bug_tracking(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """
    This node simulates bug ticket creation.
    In real life, this can create Jira / Linear / GitHub issue.
    """
    print("\n[Node] bug_tracking")

    ticket_id = "BUG-2026-001"

    return Command(
        update={
            "search_results": [f"Bug ticket created successfully: {ticket_id}"]
        },
        goto="draft_response",
    )


def draft_response(state):

    docs = state.get("search_results", [])
    context = "\n".join(docs)

    prompt = f"""
You are a customer support assistant.

Customer email:
{state['email_content']}

Relevant documentation:
{context}

Write a helpful reply using the documentation.
"""
    full_response = ""
    for chunk in llm.stream(prompt):
        if chunk.content:
            print(chunk.content, end="", flush=True)
            full_response += chunk.content   
    return {
        "draft_response": full_response
    }


def human_review(state: EmailAgentState) -> Command[Literal["send_reply", "__end__"]]:
    """
    This node pauses the workflow and waits for human approval.

    interrupt() pauses execution.
    Later, human input can resume the graph.
    """
    print("\n[Node] human_review")

    decision = interrupt(
        {
            "email_id": state["email_id"],
            "original_email": state["email_content"],
            "draft_response": state.get("draft_response", ""),
            "classification": state.get("classification", {}),
            "message": "Please approve or edit this response",
        }
    )

    # If approved, continue to send
    if decision.get("approved"):
        return Command(
            update={
                "draft_response": decision.get(
                    "edited_response",
                    state.get("draft_response", ""),
                )
            },
            goto="send_reply",
        )

    # If rejected, stop workflow
    return Command(update={}, goto="__end__")


def send_reply(state: EmailAgentState) -> dict:
    """
    This node sends the email reply.
    In production, integrate with email API here.
    """
    print("\n[Node] send_reply")
    print("Sending email reply:\n")
    print(state["draft_response"])
    print("\nEmail sent successfully.")

    return {}