import pdfplumber
import re

# Palabras clave de flujo operativo
KEYS_CFO = [
    "FLUJOS DE EFECTIVO PROCEDENTES DE (UTILIZADOS EN) ACTIVIDADES DE OPERACIÓN",
    "FLUJOS DE EFECTIVO PROCEDENTES DE ACTIVIDADES DE OPERACIÓN",
    "ACTIVIDADES DE OPERACIÓN",
    "FLUJO DE EFECTIVO OPERATIVO",
]

PREFERRED_CODES = [
    # SCVS suele poner un resumen "9820 ... actividades de operación" (método indirecto),
    # y también "9501 ... actividades de operación" (método directo)
    "9820", "9501"
]

def _to_float(s: str):
    if not s:
        return None
    s = str(s).strip()
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def extract_operating_cashflow_from_pdf(file_path: str):
    """
    Devuelve flujo operativo (CFO). Busca primero por códigos preferidos (9820/9501),
    si no, por líneas con KEYWORD y número final.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            lines = []
            for page in pdf.pages:
                text = page.extract_text() or ""
                lines.extend(text.splitlines())
    except Exception:
        return None

    # 1) Busca líneas que empiecen con código preferido y tengan un número al final
    for ln in lines:
        comp = ln.replace(" ", "")
        for code in PREFERRED_CODES:
            if comp.startswith(code):
                nums = re.findall(r"-?\d[\d\.\,]*", comp)
                if nums:
                    val = _to_float(nums[-1])
                    if val is not None:
                        return val

    # 2) Si no encontró por código, usa palabras clave
    best = None
    for ln in lines:
        up = ln.upper()
        if any(k in up for k in KEYS_CFO):
            nums = re.findall(r"-?\d[\d\.\,]*", ln.replace(" ", ""))
            if nums:
                val = _to_float(nums[-1])
                if val is not None:
                    best = val
    return best
