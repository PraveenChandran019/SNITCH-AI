from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

emb = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

db = Chroma(
    persist_directory="./db",
    embedding_function=emb
)


def store_message(text):
    db.add_texts([text])


def retrieve_context(query):
    docs = db.similarity_search(query, k=3)
    return "\n".join([d.page_content for d in docs])