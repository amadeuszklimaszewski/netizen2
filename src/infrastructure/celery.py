from celery import Celery

from src.settings import settings

app = Celery("netizen")

app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    task_serializer="pickle",
    result_serializer="pickle",
)

app.autodiscover_tasks(["src.infrastructure.email"])
