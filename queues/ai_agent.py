# queues/ai_agent.py
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import json
import math
import re
import pandas as pd

from utils.pdf_reader import extract_financial_table as extract_financial_table_from_pdf
from utils.results_reader import extract_sales_from_results_pdf
from utils.cashflow_reader import extract_operating_cashflow_from_pdf

BASE_DIR = Path(__file__).resolve().parent
GENERATED_DIR = BASE_DIR / "generated"   # aquí esperan {uid}.pdf y {uid}.json


# Json IG
def load_instagram_json(json_path: Path) -> Dict[str, Any]:
    """
    Espera:
    { "profile": {...}, "posts": [ {"likes": int, "comments": int, "caption": str, ...}, ... ] }
    Puede venir vacío: { "profile": {}, "posts": [] }
    """
    if not json_path.exists():
        return {"profile": {}, "posts": []}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"profile": {}, "posts": []}
            return {
                "profile": data.get("profile", {}) or {},
                "posts": data.get("posts", []) or []
            }
    except Exception:
        return {"profile": {}, "posts": []}


#Finanzas
FIN_LABELS = {
    "VENTAS": [
        "VENTAS", "VENTAS NETAS", "INGRESOS",
        "INGRESOS OPERACIONALES", "INGRESOS POR VENTAS"
    ],
    "FLUJO_CAJA": [
        "FLUJO DE CAJA", "FLUJO CAJA", "CASH FLOW",
        "FLUJO DE EFECTIVO", "FLUJO DE EFECTIVO OPERATIVO"
    ],
    "ACTIVOS": [
        "TOTAL ACTIVOS", "ACTIVOS", "ACTIVO TOTAL", "ACTIVO"
    ],
    "PASIVOS": [
        "TOTAL PASIVOS", "PASIVOS", "PASIVO TOTAL", "PASIVO"
    ],
    "PATRIMONIO": [
        "PATRIMONIO", "PATRIMONIO NETO", "CAPITAL"
    ],
}

def _normalize_account_name(account: str) -> str:
    if not account:
        return ""
    a = str(account).upper()
    # quita prefijos numéricos tipo '1ACTIVO', '20103CUENTAS...'
    a = re.sub(r"^\d+\s*", "", a)
    # colapsa espacios
    a = re.sub(r"\s+", " ", a).strip()
    return a

def _match_row(account: str, label_list: List[str]) -> bool:
    a = _normalize_account_name(account)
    return any(lbl in a for lbl in label_list)

def features_from_financial_df(fin_df: Optional[pd.DataFrame]) -> Dict[str, Optional[float]]:
    feats = {
        "sales": None,
        "cash_flow": None,
        "assets": None,
        "liabilities": None,
        "equity": None,
    }
    if fin_df is None or fin_df.empty:
        return feats

    for _, row in fin_df.iterrows():
        acc_raw = row.get("account", "") or ""
        acc = _normalize_account_name(acc_raw)
        val = row.get("value", None)
        if val is None:
            continue
        val = float(val)

        if _match_row(acc, FIN_LABELS["VENTAS"]):
            feats["sales"] = (feats["sales"] or 0) + val
        if _match_row(acc, FIN_LABELS["FLUJO_CAJA"]):
            feats["cash_flow"] = (feats["cash_flow"] or 0) + val
        if _match_row(acc, FIN_LABELS["ACTIVOS"]):
            feats["assets"] = (feats["assets"] or 0) + val
        if _match_row(acc, FIN_LABELS["PASIVOS"]):
            feats["liabilities"] = (feats["liabilities"] or 0) + val
        if _match_row(acc, FIN_LABELS["PATRIMONIO"]):
            feats["equity"] = (feats["equity"] or 0) + val

    # Derivado (con divisiones seguras)
    a, l, s, cf = feats["assets"], feats["liabilities"], feats["sales"], feats["cash_flow"]

    def _safe_div(num, den):
        if num is None or den is None or den == 0:
            return None
        return (float(num) + 1e-9) / (float(den) + 1e-9)

    feats["current_solvency"] = _safe_div(a, l)
    feats["asset_turnover"]   = _safe_div(s, a)
    feats["cashflow_to_debt"] = _safe_div(cf, l)

    return feats


# Social
def simple_sentiment(text: str) -> float:
    """Heurístico muy ligero de -1 a 1 basado en palabras clave (hackathon-friendly)."""
    if not text:
        return 0.0
    text = text.lower()
    pos_kw = ["excelente", "bueno", "recomendado", "rápido", "cumplen", "confiable", "genial", "agradable"]
    neg_kw = ["malo", "pésimo", "tarde", "retraso", "caro", "deficiente", "queja", "reclamo", "incumplen"]

    score = 0
    for w in pos_kw:
        if w in text:
            score += 1
    for w in neg_kw:
        if w in text:
            score -= 1
    return max(-1.0, min(1.0, score / 5.0))

def features_from_instagram(data: Dict[str, Any]) -> Dict[str, Optional[float]]:
    prof = data.get("profile", {}) or {}
    posts = data.get("posts", []) or []

    followers = prof.get("followers") or prof.get("followers_count")
    follows = prof.get("follows") or prof.get("following")
    posts_count = prof.get("posts_count") or len(posts)

    likes = []
    comments = []
    sentiments = []
    for p in posts:
        likes.append(p.get("likes", 0) or 0)
        comments.append(p.get("comments", 0) or 0)
        sentiments.append(simple_sentiment(p.get("caption", "") or ""))

    avg_likes = sum(likes) / (len(likes) or 1)
    avg_comments = sum(comments) / (len(comments) or 1)
    avg_sentiment = sum(sentiments) / (len(sentiments) or 1)

    if followers and followers > 0:
        engagement = (avg_likes + avg_comments) / float(followers)
    else:
        engagement = None

    return {
        "ig_followers": float(followers) if followers is not None else None,
        "ig_following": float(follows) if follows is not None else None,
        "ig_posts": float(posts_count) if posts_count is not None else None,
        "ig_avg_likes": float(avg_likes) if avg_likes is not None else None,
        "ig_avg_comments": float(avg_comments) if avg_comments is not None else None,
        "ig_engagement": float(engagement) if engagement is not None else None,
        "ig_sentiment": float(avg_sentiment),
    }


#Scoring
def _safe(val: Optional[float]) -> float:
    return 0.0 if (val is None or (isinstance(val, float) and math.isnan(val))) else float(val)

def _zscore(x: float, mean: float, std: float) -> float:
    if std <= 0:
        return 0.0
    return (x - mean) / std

def compute_risk_score(fin: Dict[str, Optional[float]], soc: Dict[str, Optional[float]]) -> Tuple[float, str, List[str]]:
    """
    Score 0-100 con:
    - Log-normalización y clamp de señales sociales
    - Downweight social si faltan finanzas
    - Techo del score si faltan pilares financieros
    """
    #Referencias base
    ref = {
        "sales": (200_000, 150_000),
        "cash_flow": (20_000, 15_000),
        "current_solvency": (1.5, 0.6),
        "asset_turnover": (1.0, 0.5),
        "cashflow_to_debt": (0.3, 0.2),

        
        "ig_followers_log10": (3.2, 0.6),  # ~1500 followers → log10≈3.176; std heurístico 0.6
        "ig_engagement": (0.03, 0.02),
        "ig_sentiment": (0.2, 0.3),
    }

    solv_raw = _safe(fin.get("current_solvency"))
    solv_capped = min(solv_raw, 5.0) if solv_raw > 0 else solv_raw

    # Transformaciones sociales
    followers = _safe(soc.get("ig_followers"))
    followers_log10 = math.log10(max(1.0, followers))  # log10(0) protegido
    engagement = _safe(soc.get("ig_engagement"))
    sentiment = _safe(soc.get("ig_sentiment"))

    # z-scores
    def _zcap(x, mean, std, lo=-3.0, hi=3.0):
        return max(lo, min(hi, _zscore(x, mean, std)))

    z = {
        "sales": _zscore(_safe(fin.get("sales")), *ref["sales"]),
        "cash_flow": _zscore(_safe(fin.get("cash_flow")), *ref["cash_flow"]),
        "current_solvency": _zscore(solv_capped, *ref["current_solvency"]),
        "asset_turnover": _zscore(_safe(fin.get("asset_turnover")), *ref["asset_turnover"]),
        "cashflow_to_debt": _zscore(_safe(fin.get("cashflow_to_debt")), *ref["cashflow_to_debt"]),

        # Sociales con clamp/log
        "ig_followers": _zcap(followers_log10, *ref["ig_followers_log10"]),
        "ig_engagement": _zcap(engagement, *ref["ig_engagement"]),
        "ig_sentiment": _zcap(sentiment, *ref["ig_sentiment"]),
    }

    # Ponderaciones base (equilibradas)
    w_base = {
        "sales": 0.20,
        "cash_flow": 0.20,
        "current_solvency": 0.16,
        "asset_turnover": 0.10,
        "cashflow_to_debt": 0.12,
        "ig_followers": 0.06,
        "ig_engagement": 0.10,
        "ig_sentiment": 0.06,
    }

    # Ajuste de pesos si faltan finanzas
    has_sales = fin.get("sales") not in (None, 0.0)
    has_cash = fin.get("cash_flow") not in (None, 0.0)
    financial_pillars = sum([1 if has_sales else 0, 1 if has_cash else 0])

    w = w_base.copy()
    max_score_cap = 100.0

    if financial_pillars == 0:
        # No hay ventas ni flujo: bajamos aún más el peso social y cap del score.
        w["ig_followers"] *= 0.4
        w["ig_engagement"] *= 0.4
        w["ig_sentiment"] *= 0.4
        max_score_cap = 60.0  # techo conservador sin pilares financieros
    elif financial_pillars == 1:
        # Solo hay uno de los dos: reducir sociales un poco y cap intermedio.
        w["ig_followers"] *= 0.7
        w["ig_engagement"] *= 0.7
        w["ig_sentiment"] *= 0.7
        max_score_cap = 75.0  # techo intermedio

    # Re-normaliza pesos para que sumen 1 (por prolijidad)
    w_sum = sum(w.values())
    for k in w:
        w[k] = w[k] / w_sum if w_sum > 0 else w[k]

    raw = sum(z[k] * w[k] for k in w.keys())
    # clamp del raw total, luego escalar a 0..100
    raw = max(-2.5, min(2.5, raw))
    score = (raw + 2.5) / 5.0 * 100.0
    score = min(score, max_score_cap)  # aplica techo dinámico

    # Banda por umbrales estándar
    if score >= 70:
        band = "low"
    elif score >= 40:
        band = "medium"
    else:
        band = "high"

    # Explicabilidad: top contribuciones con los pesos ajustados
    contribs = sorted([(k, z[k] * w[k]) for k in w.keys()], key=lambda x: x[1], reverse=True)
    top3 = [f"{name} {'+' if val>=0 else ''}{val:.2f}" for name, val in contribs[:3]]

    return float(round(score, 2)), band, top3



# Capital relativo
def estimate_capital_and_limit(fin: Dict[str, Optional[float]], score: float) -> Tuple[float, float]:
    sales = _safe(fin.get("sales"))
    cash_flow = _safe(fin.get("cash_flow"))
    cashflow_margin = (cash_flow / (sales + 1e-9)) if sales > 0 else 0.0

    solv = _safe(fin.get("current_solvency"))
    solv_norm = min(2.0, max(0.0, (solv - 0.5) / 1.5))  # 0..1 aprox
    base_cap = 0.5 * solv_norm + 0.5 * max(0.0, min(1.0, cashflow_margin))
    capital_relative = max(0.0, min(1.5, base_cap * (0.6 + 0.4 * (score / 100.0))))

    ratio = 0.1 + 0.2 * (score / 100.0)  # 10%-30% de ventas
    credit_limit = sales * ratio

    return float(round(capital_relative, 3)), float(round(credit_limit, 2))


# Funcion1: Agente Principal
def analyze_company(uid: str) -> Dict[str, Any]:
    generated = GENERATED_DIR
    # nombres nuevos:
    estado_path   = generated / f"{uid}-estado.pdf"    # Balance
    flujo_path    = generated / f"{uid}-flujo.pdf"     # Flujo de Efectivo
    integral_path = generated / f"{uid}-integral.pdf"  # Resultado Integral
    # fallbacks viejos por compatibilidad:
    legacy_pdf = generated / f"{uid}.pdf"
    json_path  = generated / f"{uid}.json"

    fin_df = None
    # 1) Estado de situación (balance)
    if estado_path.exists():
        fin_df = extract_financial_table_from_pdf(str(estado_path))
        if fin_df is not None and isinstance(fin_df, pd.DataFrame) and fin_df.empty:
            fin_df = None
    elif legacy_pdf.exists():
        fin_df = extract_financial_table_from_pdf(str(legacy_pdf))
        if fin_df is not None and isinstance(fin_df, pd.DataFrame) and fin_df.empty:
            fin_df = None

    fin_feats = features_from_financial_df(fin_df)

    # 2) Resultado integral → VENTAS
    if integral_path.exists():
        sales_from_er = extract_sales_from_results_pdf(str(integral_path))
        if sales_from_er is not None:
            fin_feats["sales"] = float(sales_from_er)

    # 3) Flujo de efectivo → CFO
    if flujo_path.exists():
        cfo = extract_operating_cashflow_from_pdf(str(flujo_path))
        if cfo is not None:
            fin_feats["cash_flow"] = float(cfo)

    # Social
    ig_data = load_instagram_json(json_path)
    ig_feats = features_from_instagram(ig_data)

    # Score + capital + límite
    score, band, top_factors = compute_risk_score(fin_feats, ig_feats)
    capital_relative, credit_limit = estimate_capital_and_limit(fin_feats, score)

    result = {
        "uid": uid,
        # Finanzas
        "sales": fin_feats.get("sales"),
        "cash_flow": fin_feats.get("cash_flow"),
        "assets": fin_feats.get("assets"),
        "liabilities": fin_feats.get("liabilities"),
        "equity": fin_feats.get("equity"),
        "current_solvency": fin_feats.get("current_solvency"),
        "asset_turnover": fin_feats.get("asset_turnover"),
        "cashflow_to_debt": fin_feats.get("cashflow_to_debt"),
        # Social / digital
        "ig_followers": ig_feats.get("ig_followers"),
        "ig_following": ig_feats.get("ig_following"),
        "ig_posts": ig_feats.get("ig_posts"),
        "ig_avg_likes": ig_feats.get("ig_avg_likes"),
        "ig_avg_comments": ig_feats.get("ig_avg_comments"),
        "ig_engagement": ig_feats.get("ig_engagement"),
        "ig_sentiment": ig_feats.get("ig_sentiment"),
        # Scoring
        "risk_score": score,
        "risk_band": band,
        "top_factors": top_factors,
        "capital_relative": capital_relative,
        "credit_limit_recommended": credit_limit,
    }
    return result



# Funcion2: Decision de Credito
def credit_decision(values: Dict[str, Any], requested_amount: float) -> Dict[str, Any]:
    """
    values: dict con campos de analyze_company (generalmente los lees de tu DB).
    Retorna: approved: bool, y una lista de insights accionables.
    """
    insights: List[str] = []
    band = str(values.get("risk_band", "high") or "high").lower()
    score = float(values.get("risk_score", 0) or 0.0)
    sales = _safe(values.get("sales"))
    cash_flow = _safe(values.get("cash_flow"))
    liabilities = _safe(values.get("liabilities"))
    solv = values.get("current_solvency")
    solv = float(solv) if solv is not None else None

    # DSCR aproximado: cash_flow / servicio anual de deuda (estimamos 20% del crédito)
    annual_debt_service = requested_amount * 0.20
    dscr = (cash_flow + 1e-9) / (annual_debt_service + 1e-9) if annual_debt_service > 0 else 0.0

    # Tope % de ventas por banda
    max_ratio_by_band = {"low": 0.35, "medium": 0.22, "high": 0.12}
    max_pct_sales = max_ratio_by_band.get(band, 0.12)
    sales_cap = sales * max_pct_sales if sales > 0 else 0.0

    rules = [
        score >= 40,                         # mínimo score
        requested_amount <= sales_cap,       # tope % sobre ventas
        dscr >= 1.2,                         # cobertura de servicio de deuda
    ]
    if solv is not None:
        rules.append(solv >= 1.2)            # solvencia mínima

    approved = all(rules)

    # Insights
    if score < 40:
        insights.append("Mejorar el score de riesgo; fortalece flujo de caja y reputación digital.")
    if requested_amount > sales_cap:
        insights.append(f"Reduce el monto solicitado por debajo del {int(max_pct_sales*100)}% de las ventas.")
    if dscr < 1.2:
        insights.append("Aumenta el flujo de caja operativo o extiende plazo para mejorar la cobertura (DSCR ≥ 1.2).")
    if solv is not None and solv < 1.2:
        insights.append("Mejora la solvencia (activos/pasivos ≥ 1.2).")
    if (values.get("ig_sentiment", 0) or 0) < 0.0:
        insights.append("Atiende quejas en redes para elevar el sentimiento promedio.")
    if (values.get("ig_engagement") or 0) < 0.01:
        insights.append("Incrementa el engagement (publicaciones regulares y contenido útil).")

    return {
        "approved": bool(approved),
        "requested_amount": float(requested_amount),
        "dscr_estimated": float(round(dscr, 2)),
        "max_safe_amount_by_sales": float(round(sales_cap, 2)),
        "recommended_limit": float(values.get("credit_limit_recommended") or 0.0),
        "insights": insights or (["Perfil sólido. Mantén el desempeño actual."] if approved else ["Completa datos financieros y sociales para mejorar evaluación."]),
    }


if __name__ == "__main__":
    test_uid = "demo123"
    vals = analyze_company(test_uid)
    print(">> analyze_company:", vals)
    print(">> credit_decision:", credit_decision(vals, requested_amount=15000))