from .vectorstore import upsert_texts

def ingest_application_texts(application_id: str, chunks: list[str], kind: str = "generic", extra: dict | None = None):
    texts, meta = [], []
    for i, ch in enumerate(chunks):
        texts.append(ch)
        md = {"application_id": application_id, "chunk_id": i, "doc_type": kind}
        if extra: md.update(extra)
        meta.append(md)
    return upsert_texts(texts, meta)
