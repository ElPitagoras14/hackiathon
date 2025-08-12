import pdfplumber
import re


def _to_float(x: str) -> float:
    if x is None:
        return None
    import re

    s = str(x).strip().replace(",", "")
    return float(re.sub(r"[^0-9.\-]", "", s) or 0)


def extract_sales_from_pdf(path: str) -> float:
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for tb in page.extract_tables():
                norm = [
                    [(c or "").strip() for c in row] for row in tb if any(row)
                ]
                for row in norm:
                    # Busca fila cuyo código sea 401 o cuya cuenta contenga "INGRESOS DE ACTIVIDADES ORDINARIAS"
                    cells_up = [c.upper() for c in row]
                    has_401 = any(re.fullmatch(r"401", c) for c in cells_up)
                    has_title = any(
                        "INGRESOS DE ACTIVIDADES ORDINARIAS" in c
                        for c in cells_up
                    )
                    if has_401 or has_title:
                        return _to_float(row[-1])
    return 0.0


# Alias para compatibilidad con ai_agent
def extract_sales_from_results_pdf(path: str):
    return extract_sales_from_pdf(path)
