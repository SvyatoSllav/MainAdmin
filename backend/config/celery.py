import os

from datetime import timedelta
from celery import Celery
import celery
from .settings import CELERY_BROKER_URL
from functools import wraps
from . import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('app', broker=CELERY_BROKER_URL)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, related_name='task')


class BaseTask(celery.Task):
    autoretry_for = (Exception,)
    default_retry_delay = 3
    max_retries = 5
    countdown = 5
    retry_kwargs = {}

    def __init__(self, *args, **kwargs):
        super().__init__()
        if self.autoretry_for and not hasattr(self, '_orig_run'):
            @wraps(self.run)
            def run(*args, **kwargs):
                try:
                    return self._orig_run(*args, **kwargs)
                except self.autoretry_for as exc:
                    raise self.retry(countdown=self.countdown, max_retries=self.max_retries)

            self._orig_run, self.run = self.run, run

    def __call__(self, *args, **kwargs):
        self.retries = self.request.retries
        return self.run(*args, **kwargs)

    def proccess(self, *args, **kwargs):
        raise NotImplementedError

    def life_cycle(self, *args, **kwargs):
        try:
            self.proccess(*args, **kwargs)
        except self.autoretry_for as exc:
            if self.retries >= self.max_retries:
                self.on_retries_ecxeeded()
            else:
                raise exc

    async def on_retries_ecxeeded(self):
        pass

    def run(self, *args, **kwargs):
        self.life_cycle(*args, **kwargs)
