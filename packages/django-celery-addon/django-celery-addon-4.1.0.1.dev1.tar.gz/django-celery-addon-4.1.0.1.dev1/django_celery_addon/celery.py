import django_addon.startup

from celery import Celery


django_addon.startup._setup()

from django.conf import settings  # noqa

app = Celery('django_celery_addon')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
