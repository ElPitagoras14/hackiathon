import uuid
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from loguru import logger

from log import configure_logs
from config import general_settings
from routes import router

PORT = general_settings.API_PORT

SECRET_KEY = "tu_clave_secreta"
ALGORITHM = "HS256"

configure_logs()


app = FastAPI(
    title="Hackiathon API",
    description="API for the Hackiathon project.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise Exception("Invalid token")


@app.middleware("http")
async def add_logging_context(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    username = None
    token = request.headers.get("Authorization")
    if token:
        token = token.split(" ")[-1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("username")
        except JWTError:
            username = None
    with logger.contextualize(request_id=request_id, username=username):
        response = await call_next(request)
    return response


app.include_router(router, prefix="/api")


if __name__ == "__main__":
    logger.info(f"Server running on port {PORT}")
    uvicorn.run(app="main:app", host="0.0.0.0", port=PORT, reload=True)
