import json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .config import get_settings

_PROMPT = PromptTemplate.from_template(
    """Eres analista financiero.
Features: {features}
Evidencias: {evidences}
Score: {score}
Devuelve SOLO JSON:
{{"score": {score}, "risk_level":"alto|medio|bajo", "drivers":[{{"factor":"texto","impact":+/-int,"evidence":"cita"}}], "recommendations":["...","..."]}}"""
)

def explain(features: dict, evidences: list[str], score: int) -> dict:
    s = get_settings()
    llm = ChatOpenAI(model=s.MODEL_NAME, temperature=0, api_key=s.OPENAI_API_KEY)
    res = LLMChain(llm=llm, prompt=_PROMPT).run(features=str(features), evidences=str(evidences), score=score)
    try: return json.loads(res)
    except: return {"score": score, "risk_level": "medio", "drivers": [], "recommendations": []}
