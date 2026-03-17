from typing import TypedDict, Literal, NotRequired

from langgraph.graph import StateGraph, START, END


# Define the structure for email classification
class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str


# State is the shared memory for all nodes
class EmailAgentState(TypedDict):
    # Raw email content
    email_content: str
    email_sender: str
    email_subject: str
    email_id: str

    # Classified email (filled by classify_email node)
    classification: NotRequired[EmailClassification | None]

    # Raw search/API results (filled by fetch_context node)
    search_results: NotRequired[list[str] | None]
    customer_history: NotRequired[dict | None]

    # Generated content (filled by draft_response node)
    draft_response: NotRequired[str | None]
    messages: NotRequired[list[str] | None]


# --- Node 1: Classify the email (intent, urgency, topic, summary) ---
def classify_email(state: EmailAgentState) -> dict:
    content = state["email_content"]
    subject = state["email_subject"]
    # Mock classification (replace with LLM call in production)
    intent = "billing" if "refund" in content.lower() or "bill" in content.lower() else "question"
    urgency = "high" if "urgent" in content.lower() else "medium"
    topic = subject or "general"
    summary = content[:200] + "..." if len(content) > 200 else content
    return {
        "classification": {
            "intent": intent,
            "urgency": urgency,
            "topic": topic,
            "summary": summary,
        }
    }


# --- Node 2: Fetch context (knowledge base search + CRM) ---
def fetch_context(state: EmailAgentState) -> dict:
    classification = state.get("classification") or {}
    # Mock search and CRM lookup (replace with real APIs)
    search_results = [f"Doc chunk about: {classification.get('topic', 'general')}"]
    customer_history = {
        "sender": state["email_sender"],
        "recent_tickets": 2,
        "tier": "premium",
    }
    return {"search_results": search_results, "customer_history": customer_history}


# --- Node 3: Draft the reply ---
def draft_response(state: EmailAgentState) -> dict:
    classification = state.get("classification") or {}
    search_results = state.get("search_results") or []
    customer_history = state.get("customer_history") or {}
    # Mock draft (replace with LLM using email + classification + search_results + customer_history)
    draft = (
        f"Thank you for reaching out regarding: {classification.get('topic', 'your request')}.\n\n"
        f"We've looked into your account ({customer_history.get('sender', '')}) and our resources.\n\n"
        f"Here is our response: [Draft based on {len(search_results)} context chunks.]\n\n"
        "Best regards,\nSupport"
    )
    return {"draft_response": draft, "messages": [draft]}


# --- Build the customer support email graph ---
graph = StateGraph(EmailAgentState)

graph.add_node("classify_email", classify_email)
graph.add_node("fetch_context", fetch_context)
graph.add_node("draft_response", draft_response)

graph.add_edge(START, "classify_email")
graph.add_edge("classify_email", "fetch_context")
graph.add_edge("fetch_context", "draft_response")
graph.add_edge("draft_response", END)

compiled = graph.compile()

if __name__ == "__main__":
    result = compiled.invoke({
        "email_id": "e-001",
        "email_sender": "customer@example.com",
        "email_subject": "Refund request",
        "email_content": "Hi, I need a refund for my last order. It was urgent. Thanks.",
    })
    print("Classification:", result.get("classification"))
    print("Draft response:", result.get("draft_response"))

