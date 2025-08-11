from .tools import get_financial, get_social, get_evidences, ml_prob_default
from .features import build_features
from .scoring import rule_score, combine_scores, risk_bucket
from .explain import explain

def score_application(application_id: str) -> dict:
    fin, soc = get_financial(application_id), get_social(application_id)
    feats = build_features(fin, soc)
    rules_score, drivers_rules = rule_score(feats)
    final = combine_scores(ml_prob_default(feats), rules_score)
    evid = get_evidences(application_id)
    exp = explain(feats, evid, final)
    return {
        "score": final,
        "risk_level": risk_bucket(final),
        "features": feats,
        "drivers": exp.get("drivers") or drivers_rules,
        "recommendations": exp.get("recommendations") or [],
        "evidences": evid[:3],
    }
