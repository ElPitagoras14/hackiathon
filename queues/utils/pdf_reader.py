import pdfplumber
import pandas as pd


def fill_values(row):
    values = [x for x in row[1:] if pd.notna(x)]
    while len(values) < 2:
        values.append(None)
    return pd.Series(values[:2])


def extract_financial_table(uid_or_path):
    """
    Si recibe un UID (sin extensión), busca ./<uid>.pdf.
    Si recibe una ruta completa a un PDF, usa esa ruta.
    Devuelve DataFrame con columnas ['account','code','value'].
    """
    if str(uid_or_path).lower().endswith(".pdf"):
        pdf_path = uid_or_path
    else:
        pdf_path = f"./{uid_or_path}.pdf"

    financial_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if (
                        "CUENTA" in row
                        and "CÓDIGO" in row
                        and "VALOR" in "".join([str(x) for x in row])
                    ):
                        header_index = table.index(row)
                        financial_data.extend(table[header_index + 1 :])
                        break

    df = pd.DataFrame(
        financial_data,
        columns=["account", "dummy-1", "dummy-2", "code", "value"],
    )

    df = df.dropna(how="all")
    rows = df.shape[0]
    if rows >= 2:
        df = df.iloc[
            : rows - 2, :
        ]  # limpia totales si los últimos 2 son sumas

    df[["code", "value"]] = df.apply(fill_values, axis=1)
    final_df = df[["account", "code", "value"]].copy()
    final_df["value"] = final_df["value"].astype(float)
    return final_df


# Solo se ejecuta si corres este archivo directamente
if __name__ == "__main__":
    pdf = "estado"  # ejemplo
    final_df = extract_financial_table(pdf)
    final_df.to_csv(f"{pdf}.csv", index=False)


# wrapper para compatibilidad con ai_agent
def extract_financial_table_from_pdf(path: str):
    return extract_financial_table(path)
