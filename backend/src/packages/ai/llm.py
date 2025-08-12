# backend/src/packages/ai/llm.py
import os
from typing import Dict, List
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

load_dotenv(find_dotenv(filename=".env", usecwd=True))


def _get_api_key() -> str:
    """
    Lee la API key de OPENAI/compat.
    Usa primero API_KEY del entorno. (Evita importar settings para no crear ciclos.)
    """
    key = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")
    return key or ""


def _build_prompt(metrics: Dict) -> List:
    sys = SystemMessage(content=(
        "Eres un analista de riesgos crediticios. "
        "Da recomendaciones prácticas y concisas (máx 4 bullets). "
        "Evita jerga técnica; sé específico para un negocio retail."
    ))
    human = HumanMessage(content=(
        "Métricas del negocio (JSON):\n"
        f"{metrics}\n\n"
        "Genera sugerencias de mejora en ventas, flujo de caja y reputación online. "
        "No inventes datos; usa solo lo dado."
    ))
    return [sys, human]


def generate_insights(metrics: Dict) -> List[str]:
    """
    Llama al LLM para generar insights a partir de las métricas.
    Devuelve una lista de strings (bullets).
    Si no hay API key, devuelve un fallback simple.
    """
    api_key = _get_api_key()
    if not api_key:
        # Fallback sin LLM
        tips = []
        if metrics.get("ig_engagement", 0) < 0.01:
            tips.append("Publica 3–4 veces/semana con llamados a la acción y responde comentarios en 24h.")
        if metrics.get("current_solvency", 0) < 1.5:
            tips.append("Negocia plazos con proveedores para aliviar el pasivo corriente y mejorar solvencia.")
        if metrics.get("asset_turnover", 0) < 1:
            tips.append("Optimiza inventario: rota lentos con bundles/descuentos para subir la rotación de activos.")
        if metrics.get("cash_flow", 0) <= 0:
            tips.append("Prioriza cobranza a crédito y recorta gastos no esenciales por 60–90 días.")
        return tips or ["Mantén disciplina de caja semanal y mide márgenes por línea de producto."]

    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-4o-mini",
        temperature=0.3,
    )
    msgs = _build_prompt(metrics)
    out = llm.invoke(msgs).content.strip()

    # Normaliza a lista de bullets
    lines = [l.strip("•- ").strip() for l in out.splitlines() if l.strip()]
    # Filtra vacíos
    lines = [l for l in lines if l]
    # Máximo 4
    return lines[:4]
