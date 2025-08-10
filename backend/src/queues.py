from celery import Celery


celery_app = Celery(
    "worker_client",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)
