import pdfplumber
import re


def _to_float(x: str) -> float:
    if x is None:
        return None
    s = str(x).strip().replace(",", "")
    return float(re.sub(r"[^0-9.\-]", "", s) or 0)


def extract_operating_cashflow_from_pdf(path: str) -> float:
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for tb in tables:
                # Normalizamos celdas
                norm = [
                    [(c or "").strip() for c in row] for row in tb if any(row)
                ]
                for row in norm:
                    joined = " ".join(row).upper()
                    # match por codigo 9820
                    if re.search(r"(^|\s)9820(\s|$)", joined):
                        # toma el último campo como VALOR
                        val = _to_float(row[-1])
                        if val != 0:
                            return val
                    # fallback: por nombre
                    if (
                        "FLUJOS DE EFECTIVO NETOS PROCEDENTES DE (UTILIZADOS EN) ACTIVIDADES DE OPERACIÓN"
                        in joined
                    ):
                        val = _to_float(row[-1])
                        if val != 0:
                            return val
    return None
