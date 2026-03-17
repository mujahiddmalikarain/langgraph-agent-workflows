# LangGraph Agent Workflows

LangGraph-based agent workflows: simple graph demo, "Thinking in LangGraph" email example, and a **customer support email agent** with classification, RAG, human-in-the-loop, and durable execution.

---

## Repository structure

```
langgraph-agent-workflows/
├── README.md                 # This file
├── .gitignore
├── main.py                   # Simple LangGraph demo (StateGraph, one node)
├── thinking-langgraph.py     # Customer support email agent (single-file version)
└── langgraph-email-agent/    # Full email agent application
    ├── main.py               # Entry point: invoke graph with initial state & config
    ├── graph.py              # Workflow definition: nodes, edges, checkpointer
    ├── state.py              # EmailAgentState & EmailClassification (TypedDict)
    ├── nodes.py              # Node logic: read, classify, search, bug, draft, review, send
    ├── requirements.txt
    ├── .env                  # API keys (not committed)
    ├── docs/
    │   └── support_dccs.txt   # Support docs for RAG
    └── rag/
        ├── ingest.py         # Ingest docs into FAISS vector store
        └── retriver.py       # Load FAISS + OpenAI embeddings, retrieve_docs()
```

---

## Architecture: Customer support email agent

The **langgraph-email-agent** app models a support pipeline as a LangGraph workflow:

| Layer        | Role |
|-------------|------|
| **State**   | `EmailAgentState` in `state.py`: email fields, classification, search_results, customer_history, draft_response, messages. |
| **Graph**   | `graph.py`: `StateGraph(EmailAgentState)`, nodes, edges, `MemorySaver` checkpointer, `RetryPolicy` on search/bug nodes. |
| **Nodes**   | `nodes.py`: `read_email` → `classify_intent` (LLM) → branch to `search_documentation` \| `bug_tracking` \| `human_review` \| `draft_response` → `draft_response` → `human_review` (interrupt) → `send_reply`. |
| **RAG**     | `rag/retriver.py`: FAISS + OpenAI embeddings; `retrieve_docs(query)` used in `search_documentation`. |
| **Run**     | `main.py`: `app.invoke(initial_state, config)` with `thread_id`; handles `__interrupt__` and resume via `Command(resume=...)`. |

Flow summary:

1. **read_email** – Reads email from state (in production: Gmail/Outlook).
2. **classify_intent** – LLM classifies intent (question, bug, billing, feature, complex), urgency, topic, summary; returns `Command(goto=...)` to route.
3. **search_documentation** – RAG over support docs (with retry).
4. **bug_tracking** – Simulated bug ticket creation (with retry).
5. **draft_response** – Builds reply from state (classification + search/customer data).
6. **human_review** – `interrupt()` for approval/edit; workflow resumes with `Command(resume=...)`.
7. **send_reply** – Final send (simulated).

---

## Setup

### Root / simple demos

```bash
pip install langgraph langchain langchain-openai python-dotenv
# Optional: set OPENAI_API_KEY in .env
python main.py
# or
python thinking-langgraph.py
```

### Email agent (`langgraph-email-agent`)

```bash
cd langgraph-email-agent
pip install -r requirements.txt
```

Create `.env` (see `.env.example` if present) with:

- `OPENAI_API_KEY`

Then:

1. **Ingest docs (one-time):**  
   `python -m rag.ingest`  
   (writes FAISS index to `./fasiss_db/` or path used in `rag/retriver.py`.)

2. **Run agent:**  
   `python main.py`  
   (from `langgraph-email-agent/` so `./fasiss_db` and `rag` resolve correctly.)

---

## Requirements (email agent)

- Python 3.10+
- LangGraph, LangChain, langchain-community, langchain-openai
- OpenAI API key
- FAISS index under `langgraph-email-agent/` (e.g. `fasiss_db/`) after running ingest

---

## License

MIT (or your choice).
