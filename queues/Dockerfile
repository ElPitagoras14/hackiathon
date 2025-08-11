FROM python:3.10-slim

# Instala librerías necesarias para Xvfb, Chromium y compilación (psycopg2)
RUN apt-get update && apt-get install -y \
    xvfb x11-utils x11-xserver-utils x11-apps \
    wget curl libnss3 libatk-bridge2.0-0 libgtk-3-0 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 \
    dbus-x11 \
    build-essential libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Evita buffering para que los logs salgan en tiempo real
ENV PYTHONUNBUFFERED=1

# Instala librerías Python necesarias (sin 'asyncio' ni 'dotenv', que debe ser 'python-dotenv')
RUN pip install --no-cache-dir \
    playwright \
    langchain_openai \
    langchain_core \
    playwright_stealth \
    pyvirtualdisplay \
    python-dotenv \
    pydantic_settings \
    sqlalchemy \
    psycopg2 \
    redis \
    loguru \
    filelock \
    celery

# Instala navegadores y dependencias de Playwright para Chromium
RUN playwright install chromium
RUN playwright install-deps chromium

# Copia el código fuente al contenedor
WORKDIR /app
COPY . .

# Permite ejecutar celery como root (si lo necesitas)
ENV C_FORCE_ROOT=true

# Comando por defecto para correr tu app o worker de Celery
CMD ["python", "main.py"]
