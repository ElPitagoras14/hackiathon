from celery import Celery

from config import general_settings

REDIS_URL = general_settings.REDIS_URL

celery_app = Celery(
    "worker_client",
    broker=f"{REDIS_URL}/0",
    backend=f"{REDIS_URL}/1",
)
