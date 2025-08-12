# backend/src/packages/ai/agent.py
from typing import Dict, Any
from packages.ai.llm import generate_insights
from packages.utils.results_reader import extract_sales_from_pdf
from packages.utils.cashflow_reader import extract_operating_cashflow_from_pdf
from packages.utils.pdf_reader import extract_financial_table_from_pdf
from packages.utils.social_reader import read_social_json  # si no lo tienes, usa tu reader actual

def analyze_company(uid: str) -> Dict[str, Any]:
    # Rutas (ajústalas a tu estructura de generated/)
    base = "generated"
    res_pdf = f"{base}/{uid}-integral.pdf"
    cash_pdf = f"{base}/{uid}-flujo.pdf"
    bal_pdf = f"{base}/{uid}-estado.pdf"
    social_json = f"{base}/{uid}.json"

    # Extract
    sales = extract_sales_from_pdf(res_pdf)                 # float
    cash_flow = extract_operating_cashflow_from_pdf(cash_pdf)
    df = extract_financial_table_from_pdf(bal_pdf)          # DataFrame con 'code' y 'value'
    assets = float(df.loc[df["code"] == "1", "value"].iloc[0])
    liabilities = float(df.loc[df["code"] == "2", "value"].iloc[0])
    equity = float(df.loc[df["code"] == "3", "value"].iloc[0])

    # Ratios básicos
    current_solvency = assets / max(liabilities, 1e-6)
    asset_turnover = sales / max(assets, 1e-6)
    cashflow_to_debt = cash_flow / max(liabilities, 1e-6)

    # Social (ajusta a tu estructura real)
    social = read_social_json(social_json)
    followers = float(social["profile"]["follower_num"])
    following = float(social["profile"]["following_num"])
    posts = float(social["profile"]["post_num"])
    likes = sum(int(p.get("likes", 0)) for p in social["posts"][:12]) / max(len(social["posts"][:12]), 1)
    comments = sum(len(p.get("comments", [])) for p in social["posts"][:12]) / max(len(social["posts"][:12]), 1)
    engagement = (likes + comments) / max(followers, 1.0)

    # Arma payload base
    payload = {
        "uid": uid,
        "sales": sales,
        "cash_flow": cash_flow,
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "current_solvency": current_solvency,
        "asset_turnover": asset_turnover,
        "cashflow_to_debt": cashflow_to_debt,
        "ig_followers": followers,
        "ig_following": following,
        "ig_posts": posts,
        "ig_avg_likes": likes,
        "ig_avg_comments": comments,
        "ig_engagement": engagement,
    }

    # LLM: recomendaciones
    payload["insights"] = generate_insights(payload)
    return payload

def credit_decision(vals: Dict[str, Any], requested_amount: float) -> Dict[str, Any]:
    # Reglas sencillas (puedes afinar)
    ok_cf = vals["cash_flow"] > 0
    ok_solv = vals["current_solvency"] >= 1.2
    ok_turn = vals["asset_turnover"] >= 0.2

    approved = bool(ok_cf and ok_solv and ok_turn)
    # límite por ventas (10–35% como ejemplo)
    max_by_sales = max(0.1 * vals["sales"], min(0.35 * vals["sales"], 1e9))
    recommended = min(max_by_sales, vals["equity"] * 0.8)

    return {
        "approved": approved,
        "requested_amount": float(requested_amount),
        "dscr_estimated": round(vals["cash_flow"] / max(requested_amount, 1.0), 2),
        "max_safe_amount_by_sales": round(max_by_sales, 2),
        "recommended_limit": round(max(recommended, 0.0), 2),
        # Usa los insights del LLM (ya los generamos en analyze_company)
        "insights": vals.get("insights", []),
    }
