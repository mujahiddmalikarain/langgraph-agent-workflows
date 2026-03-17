from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import RetryPolicy

from state import EmailAgentState
from nodes import (
    read_email,
    classify_intent,
    search_documentation,
    bug_tracking,
    draft_response,
    human_review,
    send_reply,
)

# Create graph object with shared state
workflow = StateGraph(EmailAgentState)

# Add nodes
workflow.add_node("read_email", read_email)
workflow.add_node("classify_intent", classify_intent)

# Add retry policy to nodes that may fail because of API/network
workflow.add_node(
    "search_documentation",
    search_documentation,
    retry_policy=RetryPolicy(max_attempts=3),
)

workflow.add_node(
    "bug_tracking",
    bug_tracking,
    retry_policy=RetryPolicy(max_attempts=3),
)

workflow.add_node("draft_response", draft_response)
workflow.add_node("human_review", human_review)
workflow.add_node("send_reply", send_reply)

# Route after classification based on intent (node updates state["classification"])
def route_after_classify(state):
    c = state.get("classification") or {}
    intent = c.get("intent", "question")
    if intent == "bug":
        return "bug_tracking"
    if intent in ("billing", "complex"):
        return "human_review"
    if intent == "question":
        return "search_documentation"
    return "draft_response"

# Fixed and conditional edges
workflow.add_edge(START, "read_email")
workflow.add_edge("read_email", "classify_intent")
workflow.add_conditional_edges("classify_intent", route_after_classify)
workflow.add_edge("search_documentation", "draft_response")
workflow.add_edge("bug_tracking", "draft_response")
workflow.add_edge("draft_response", "human_review")
workflow.add_conditional_edges(
    "human_review",
    lambda s: "send_reply" if s.get("draft_response") else "__end__",
    {"send_reply": "send_reply", "__end__": END},
)
workflow.add_edge("send_reply", END)

# Durable execution:
# MemorySaver stores state checkpoints so the graph can resume later
checkpointer = MemorySaver()

# Compile graph with checkpointer
app = workflow.compile(checkpointer=checkpointer)