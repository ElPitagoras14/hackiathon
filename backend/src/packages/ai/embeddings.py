from langchain_openai import OpenAIEmbeddings
from .config import get_settings

def build_embedder():
    s = get_settings()
    return OpenAIEmbeddings(model=s.EMBEDDING_MODEL, api_key=s.OPENAI_API_KEY)
