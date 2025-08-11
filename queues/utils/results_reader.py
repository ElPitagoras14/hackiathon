import pdfplumber
import re

# Palabras clave típicas de SCVS para ingresos/ventas
KEYS_SALES = [
    "INGRESOS DE ACTIVIDADES ORDINARIAS",
    "VENTAS", "VENTAS NETAS",
    "INGRESOS", "INGRESOS OPERACIONALES",
    "INGRESOS POR VENTAS"
]

def _to_float(s: str):
    if not s:
        return None
    s = str(s).strip()
    # Normaliza separadores: quita puntos de miles y usa punto decimal
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def extract_sales_from_results_pdf(file_path: str):
    """
    Lee 'Estado de Resultado Integral' y devuelve un float con VENTAS/INGRESOS.
    Estrategia: buscar la línea con KEY y tomar el último número encontrado en esa línea.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            lines = []
            for page in pdf.pages:
                text = page.extract_text() or ""
                lines.extend(text.splitlines())
    except Exception:
        return None

    # Intenta primero "INGRESOS DE ACTIVIDADES ORDINARIAS"
    best = None
    for ln in lines:
        up = ln.upper()
        if any(k in up for k in KEYS_SALES):
            # toma el último número de la línea
            nums = re.findall(r"-?\d[\d\.\,]*", ln.replace(" ", ""))
            if nums:
                val = _to_float(nums[-1])
                if val is not None:
                    best = val
    return best
