from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (langgraph-email-agent/) so it works when run as python -m rag.ingest
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# Step 1: set up the documents
project_root = Path(__file__).resolve().parent.parent
loader = TextLoader(str(project_root / "docs" / "support_dccs.txt"))
docs=loader.load()
print(docs)


#split the documents into chunks

text_splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=200) #chunk overlap mean connection between chunks like chnk1=a,b,c and chnk2=c,d,e then chunk overlap is c


docs = text_splitter.split_documents(docs)

#create embeddings

embeddings=OpenAIEmbeddings(model="text-embedding-3-small")

# Create vector store (FAISS does not take persist_directory in from_documents)
vectorstore = FAISS.from_documents(docs, embeddings)

# Save to disk so retriever can load it later (same path as in retriver.py)
vectorstore.save_local(str(project_root / "fasiss_db"))

print("Vector store created and persisted.")