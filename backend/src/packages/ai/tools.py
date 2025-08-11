def get_financial(application_id: str) -> dict:
    # TODO: conéctalo a tu parser real/DB
    return {"ventas_12m": 80000, "pasivo_total": 60000, "activo_total": 90000}

def get_social(application_id: str) -> dict:
    # TODO: conéctalo a scraping real
    return {"avg_sentiment": -0.1, "review_count": 34, "posts_30d": 12}

def get_evidences(application_id: str) -> list[str]:
    from .retrieval import build_retriever
    docs = build_retriever().get_relevant_documents(f"application:{application_id}")
    return [d.page_content for d in docs[:5]]

def ml_prob_default(features: dict) -> float | None:
    # TODO: conectar modelo cuando lo tengan
    return None
