FROM python:3.12

WORKDIR /app

COPY src /app/src
COPY requirements.txt /app

RUN pip install --default-timeout=1000 -r requirements.txt

EXPOSE ${API_PORT}

CMD ["sh", "-c", "cd src && python main.py"]