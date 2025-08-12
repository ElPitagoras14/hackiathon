from pathlib import Path
import json
from statistics import mean
from utils.results_reader import extract_sales_from_pdf
from utils.cashflow_reader import extract_operating_cashflow_from_pdf
from utils.pdf_reader import extract_financial_table_from_pdf

SCORING_WEIGHTS = {
    "Flujo de caja promedio (últimos 6 meses)": 0.20,
    "Nivel de endeudamiento": 0.10,
    "Variabilidad en ingresos": 0.10,
    "Reseñas en plataformas (Google, Facebook)": 0.10,
    "Actividad en redes sociales": 0.05,
    "Historial con proveedores": 0.10,
    "Recomendaciones de clientes": 0.05,
    "Cumplimiento en pagos": 0.15,
}

def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, float(x)))

def _safe_div(a, b):
    try:
        if b is None or float(b) == 0.0:
            return None
        return float(a) / float(b)
    except:
        return None

def _norm_cashflow(cash_flow, sales):
    if cash_flow is None or sales is None or sales <= 0:
        return 0.0
    if cash_flow <= 0:
        return 0.0
    return _clamp(cash_flow / (0.30 * sales))

def _score_leverage(liabilities, assets):
    if not assets or assets <= 0 or liabilities is None:
        return 0.0
    ratio = liabilities / assets
    if ratio <= 0.2:
        return 1.0
    if ratio >= 1.5:
        return 0.0
    return _clamp(1 - (ratio - 0.2) / (1.5 - 0.2))

def _score_revenue_variability(std_over_mean=None):
    if std_over_mean is None:
        return 0.70
    return _clamp(1 - (std_over_mean / 0.50))

def _score_reviews_nlp(sentiment):
    if sentiment is None:
        return 0.50
    return _clamp((sentiment + 1.0) / 2.0)

def _score_social_activity(posts_last_7_days=None):
    if posts_last_7_days is None:
        return 0.75
    return _clamp(posts_last_7_days / 8.0)

def _score_suppliers_history(value=None):
    return 0.80 if value is None else _clamp(value)

def _score_client_recos_nlp(value=None):
    return 0.65 if value is None else _clamp(value)

def _score_payment_behavior(value=None):
    return 0.95 if value is None else _clamp(value)

def _load_social_json(path: Path):
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return None

    profile = data.get("profile", {})
    followers = profile.get("followers") or profile.get("follower_num")
    follows = profile.get("follows") or profile.get("following_num")
    posts_count = profile.get("posts_count") or profile.get("post_num")
    name = profile.get("name")
    is_verified = profile.get("is_verified")
    desc = profile.get("description")

    posts = data.get("posts", [])
    likes_list = []
    comments_counts = []
    last_days = []

    for p in posts:
        lk = p.get("likes")
        if lk is not None:
            try:
                likes_list.append(float(lk))
            except:
                pass
        c = p.get("comments")
        if isinstance(c, list):
            comments_counts.append(len(c))
        elif isinstance(c, (int, float)):
            comments_counts.append(float(c))
        if isinstance(p.get("last_day"), (int, float)):
            last_days.append(int(p["last_day"]))

    avg_likes = mean(likes_list) if likes_list else 0.0
    avg_comments = mean(comments_counts) if comments_counts else 0.0
    followers_f = float(followers) if followers not in (None, 0, "0") else None
    engagement = ((avg_likes + avg_comments) / followers_f) if followers_f else 0.0
    posts_last_7 = sum(1 for d in last_days if 0 <= d <= 6) if last_days else None

    return {
        "ig_followers": followers_f or 0.0,
        "ig_following": float(follows) if follows is not None else 0.0,
        "ig_posts": float(posts_count) if posts_count is not None else float(len(posts)),
        "ig_avg_likes": float(avg_likes),
        "ig_avg_comments": float(avg_comments),
        "ig_engagement": float(engagement),
        "ig_sentiment": 0.0,
        "_posts_last_7": posts_last_7,
        "_raw": data,
        "_name": name,
        "_verified": bool(is_verified) if is_verified is not None else None,
        "_description": desc,
    }

def _extract_balance_items(df):
    assets = liabilities = equity = None
    try:
        assets = float(df.loc[df["code"] == "1"].iloc[0]["value"])
    except:
        pass
    try:
        liabilities = float(df.loc[df["code"] == "2"].iloc[0]["value"])
    except:
        pass
    try:
        equity = float(df.loc[df["code"] == "3"].iloc[0]["value"])
    except:
        pass
    return assets, liabilities, equity

def _estimate_posts_last_7_days(social_json):
    if not social_json:
        return None
    return social_json.get("_posts_last_7")

def _compute_scoring_breakdown(vals, social_json=None, overrides=None):
    overrides = overrides or {}
    cash_flow = vals.get("cash_flow")
    sales = vals.get("sales")
    assets = vals.get("assets")
    liabilities = vals.get("liabilities")
    sentiment = vals.get("ig_sentiment")
    posts_last_7 = _estimate_posts_last_7_days(social_json)

    candidates = {
        "Flujo de caja promedio (últimos 6 meses)": _norm_cashflow(cash_flow, sales),
        "Nivel de endeudamiento": _score_leverage(liabilities, assets),
        "Variabilidad en ingresos": _score_revenue_variability(None),
        "Reseñas en plataformas (Google, Facebook)": _score_reviews_nlp(sentiment),
        "Actividad en redes sociales": _score_social_activity(posts_last_7),
        "Historial con proveedores": _score_suppliers_history(None),
        "Recomendaciones de clientes": _score_client_recos_nlp(None),
        "Cumplimiento en pagos": _score_payment_behavior(None),
    }

    breakdown = []
    total = 0.0
    for factor, weight in SCORING_WEIGHTS.items():
        score = overrides.get(factor, candidates.get(factor, 0.0))
        score = _clamp(score)
        contribution = round(weight * score, 6)
        total += contribution
        breakdown.append({
            "factor": factor,
            "weight": round(weight, 4),
            "score": round(score, 4),
            "contribution": contribution
        })

    total = _clamp(total)
    return breakdown, total

def analyze_company(uid: str):
    base = Path("generated")
    estado_pdf = base / f"{uid}-estado.pdf"
    flujo_pdf = base / f"{uid}-flujo.pdf"
    integral_pdf = base / f"{uid}-integral.pdf"
    social_json_path = base / f"{uid}.json"

    sales = extract_sales_from_pdf(str(integral_pdf)) if integral_pdf.exists() else None
    cash_flow = extract_operating_cashflow_from_pdf(str(flujo_pdf)) if flujo_pdf.exists() else None

    assets = liabilities = equity = None
    if estado_pdf.exists():
        df = extract_financial_table_from_pdf(str(estado_pdf))
        assets, liabilities, equity = _extract_balance_items(df)

    current_solvency = _safe_div(assets, liabilities) if assets and liabilities else None
    asset_turnover = _safe_div(sales, assets) if assets else None
    cashflow_to_debt = _safe_div(cash_flow, liabilities) if liabilities else None

    social = _load_social_json(social_json_path) or {}
    ig_followers = social.get("ig_followers", 0.0)
    ig_following = social.get("ig_following", 0.0)
    ig_posts = social.get("ig_posts", 0.0)
    ig_avg_likes = social.get("ig_avg_likes", 0.0)
    ig_avg_comments = social.get("ig_avg_comments", 0.0)
    ig_engagement = social.get("ig_engagement", 0.0)
    ig_sentiment = social.get("ig_sentiment", 0.0)

    vals = {
        "uid": uid,
        "sales": sales or 0.0,
        "cash_flow": cash_flow,
        "assets": assets or 0.0,
        "liabilities": liabilities or 0.0,
        "equity": equity or 0.0,
        "current_solvency": current_solvency if current_solvency is not None else 0.0,
        "asset_turnover": asset_turnover if asset_turnover is not None else 0.0,
        "cashflow_to_debt": cashflow_to_debt,
        "ig_followers": ig_followers,
        "ig_following": ig_following,
        "ig_posts": ig_posts,
        "ig_avg_likes": ig_avg_likes,
        "ig_avg_comments": ig_avg_comments,
        "ig_engagement": ig_engagement,
        "ig_sentiment": ig_sentiment,
        "_social_raw": social.get("_raw"),
    }

    breakdown, total_score = _compute_scoring_breakdown(vals, social_json=social)
    vals["scoring_breakdown"] = breakdown
    vals["risk_score"] = round(total_score * 100.0, 2)
    vals["risk_band"] = "low" if vals["risk_score"] >= 80 else ("medium" if vals["risk_score"] >= 60 else "high")

    top = sorted(breakdown, key=lambda x: x["contribution"], reverse=True)[:3]
    vals["top_factors"] = [f"{x['factor']} {x['score']:+.2f}" for x in top]
    vals["capital_relative"] = round(_safe_div(vals["equity"], vals["assets"]) or 0.0, 3)

    base_limit = (vals["sales"] or 0.0) * 0.35
    adj = 0.5 + 0.5 * total_score
    vals["credit_limit_recommended"] = round(base_limit * adj, 2)

    return vals

def credit_decision(analysis_payload: dict, requested_amount: float):
    sales = float(analysis_payload.get("sales", 0.0) or 0.0)
    cash_flow = float(analysis_payload.get("cash_flow", 0.0) or 0.0)
    recommended = float(analysis_payload.get("credit_limit_recommended", 0.0) or 0.0)

    max_by_sales = round(sales * 0.35, 2)
    debt_service = max(requested_amount * 0.30, 1.0)
    dscr = round(cash_flow / debt_service, 2) if debt_service else 0.0

    approved = (requested_amount <= recommended) and (dscr >= 1.2)
    insights = []
    if requested_amount > max_by_sales:
        insights.append("Reduce el monto solicitado por debajo del 35% de las ventas.")
    if dscr < 1.2:
        insights.append("Aumenta el flujo de caja operativo o extiende plazo para mejorar la cobertura (DSCR ≥ 1.2).")
    if analysis_payload.get("ig_engagement", 0.0) < 0.01:
        insights.append("Incrementa el engagement (publicaciones regulares y contenido útil).")
    if not insights:
        insights.append("Perfil sólido; mantén disciplina de cobranza y control de gastos.")

    return {
        "approved": approved,
        "requested_amount": float(requested_amount),
        "dscr_estimated": dscr,
        "max_safe_amount_by_sales": max_by_sales,
        "recommended_limit": recommended,
        "insights": insights,
    }