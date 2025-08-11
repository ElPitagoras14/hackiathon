def build_features(financial: dict | None, social: dict | None, extras: dict | None = None) -> dict:
    f, v, s = {}, (financial or {}), (social or {})
    if v.get("ventas_12m") is not None: f["ventas_12m"] = float(v["ventas_12m"])
    if v.get("activo_total") and v.get("pasivo_total"):
        try: f["ratio_ap"] = float(v["pasivo_total"]) / float(v["activo_total"])
        except: pass
    if s.get("avg_sentiment") is not None: f["avg_sentiment"] = float(s["avg_sentiment"])
    if s.get("review_count") is not None: f["review_count"] = int(s["review_count"])
    if s.get("posts_30d") is not None: f["posts_30d"] = int(s["posts_30d"])
    if extras: f.update(extras)
    return f
