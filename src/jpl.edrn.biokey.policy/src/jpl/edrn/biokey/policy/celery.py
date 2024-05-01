# encoding: utf-8

'''🧬🔑 BioKey task queues using Celery.'''

from celery import Celery
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jpl.edrn.biokey.policy.settings.ops')
app = Celery('BioKey')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
