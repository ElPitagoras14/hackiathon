from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from .embeddings import build_embedder
from .config import get_settings

def get_chroma():
    s = get_settings()
    return Chroma(
        collection_name="company_texts",
        embedding_function=build_embedder(),
        persist_directory=s.CHROMA_PERSIST_DIR
    )

def upsert_texts(texts: list[str], metadata: list[dict]):
    vs = get_chroma()
    docs = [Document(page_content=t, metadata=m) for t, m in zip(texts, metadata)]
    vs.add_documents(docs)
    vs.persist()
    return len(docs)
