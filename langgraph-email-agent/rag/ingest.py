from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
#step 1: set up the documents
#load the documents
loader=TextLoader("docs/support_dccs.txt")
docs=loader.load()
print(docs)


#split the documents into chunks

text_splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=200) #chunk overlap mean connection between chunks like chnk1=a,b,c and chnk2=c,d,e then chunk overlap is c


docs = text_splitter.split_documents(docs)

#create embeddings

embeddings=OpenAIEmbeddings(model="text-embedding-3-small")

#create a vector store

vectorstore=FAISS.from_documents(
      docs,
      embeddings,
      persist_directory="./fasiss_db" #persist the vector store to a file

)

vectorstore.persist()

print("Vector store created and persisted")