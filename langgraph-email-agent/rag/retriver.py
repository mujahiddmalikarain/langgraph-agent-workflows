from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root so API key is set before OpenAI calls
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Load the vector store (same path as in rag/ingest.py)
project_root = Path(__file__).resolve().parent.parent
folder_path = str(project_root / "fasiss_db")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.load_local(
    folder_path,
    embeddings,
    allow_dangerous_deserialization=True,  # required for pickle; only use with trusted index
)

#create a retriever

retriever=vectorstore.as_retriever(search_type="similarity",search_kwargs={"k":5})

def retrieve_docs(query: str):
    docs = retriever.invoke(query)
    return [doc.page_content for doc in docs]
      
