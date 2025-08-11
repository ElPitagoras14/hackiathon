def rule_score(features: dict) -> tuple[int, list[dict]]:
    score = 50; drivers=[]
    if features.get("ventas_12m", 0) > 50000: score += 10; drivers.append({"factor":"ventas","impact":+10})
    if features.get("avg_sentiment", 0) < -0.3: score -= 15; drivers.append({"factor":"reputación","impact":-15})
    if features.get("ratio_ap", 0) > 1.5: score -= 20; drivers.append({"factor":"apalancamiento","impact":-20})
    if features.get("review_count", 0) >= 20: score += 5; drivers.append({"factor":"señales_sociales","impact":+5})
    return max(0,min(100,score)), drivers

def combine_scores(ml_prob_default: float | None, rules_score: int) -> int:
    if ml_prob_default is None: return rules_score
    score_ml = int(round((1 - ml_prob_default) * 100))
    return max(0, min(100, int(round(0.6*score_ml + 0.4*rules_score))))

def risk_bucket(score: int) -> str:
    return "alto" if score<=40 else "medio" if score<=70 else "bajo"
