from typing import TypedDict, Literal, Optional


# This is the structured output for classification
class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str


# This is the global shared state of the graph
class EmailAgentState(TypedDict):
    # Original email data
    email_content: str
    sender_email: str
    email_id: str

    # LLM classification result
    classification: Optional[EmailClassification]

    # Data fetched from docs / systems
    search_results: Optional[list[str]]
    customer_history: Optional[dict]

    # Final draft prepared by AI
    draft_response: Optional[str]

    # Useful for debugging/logging
    messages: Optional[list[str]]