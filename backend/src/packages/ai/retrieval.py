from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from .vectorstore import get_chroma
from .config import get_settings

def build_retriever(k: int = 5):
    return get_chroma().as_retriever(search_kwargs={"k": k})

def build_qa_chain():
    s = get_settings()
    llm = ChatOpenAI(model=s.MODEL_NAME, temperature=0, api_key=s.OPENAI_API_KEY)
    return RetrievalQA.from_chain_type(llm=llm, retriever=build_retriever(), chain_type="stuff")
