from datetime import datetime, timedelta, timezone
from jose import jwt
from loguru import logger

from databases.postgres import DatabaseSession, User

from .utils import get_hash, verify_password
from .config import auth_settings
from .responses import Tokens


SECRET_KEY = auth_settings.SECRET_KEY
ALGORITHM = auth_settings.ALGORITHM
ACCESS_TOKEN_EXP_MIN = auth_settings.ACCESS_TOKEN_EXP_MIN
REFRESH_TOKEN_EXP_DAY = auth_settings.REFRESH_TOKEN_EXP_DAY


def create_access_token(user_data: dict):
    payload = {
        **user_data,
        "type": "access",
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXP_MIN),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_data: dict):
    payload = {
        **user_data,
        "type": "refresh",
        "exp": datetime.now(timezone.utc)
        + timedelta(days=REFRESH_TOKEN_EXP_DAY),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def login_controller(email: str, password: str):
    logger.debug(f"User {email} is trying to log in")
    with DatabaseSession() as db:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None, "User not found"
        if not verify_password(password, user.password):
            return None, "Invalid password"
        logger.info(f"User {email} logged in")
        access_token = create_access_token(
            {
                "id": str(user.id),
                "email": user.email,
            },
        )
        refresh_token = create_refresh_token(
            {
                "id": str(user.id),
                "email": user.email,
            },
        )
        return Tokens(access=access_token, refresh=refresh_token), None


def register_controller(email: str, password: str):
    logger.debug(f"User {email} is trying to register")
    with DatabaseSession() as db:
        user = db.query(User).filter(User.email == email).first()
        if user:
            return None, "User already exists"
        hashed_password = get_hash(password)
        user = User(email=email, password=hashed_password)
        db.add(user)
        db.commit()
        logger.info(f"User {email} registered")
        return "User registered", None
