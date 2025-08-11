import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

# Calcular ruta absoluta al .env en el root
root_env_path = Path(__file__).resolve().parent.parent / ".env"

# Cargar ese .env
load_dotenv(dotenv_path=root_env_path)

# Leer la API key
api_key = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
if not api_key:
    raise RuntimeError("Falta OPENAI_API_KEY o API_KEY en .env")

# Crear cliente
client = OpenAI(api_key=api_key)

# Probar llamada
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Dime un chiste corto sobre PYMEs"}],
)

print(resp.choices[0].message)
