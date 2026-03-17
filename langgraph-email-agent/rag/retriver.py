from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

#load the vector store

vectorstore = FAISS.load_local(
    persist_directory="./fasiss_db",
    embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
)

#create a retriever

retriever=vectorstore.as_retriever(search_type="similarity",search_kwargs={"k":5})

def retrieve_docs(query:str):
      docs=retriever.get_relevant_documents(query)
      return [doc.page_content for doc in docs]
      
