# import absolute imports from the future, so that our celery.py module won’t clash with the library:
from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# set the default DJANGO_SETTINGS_MODULE environment variable for the celery command-line program:
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Stemweb.settings')

# instance of class Celery:
celery_app = Celery('Stemweb')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks(settings.INSTALLED_APPS)    # This way we shouldn’t have to manually add the individual modules to the CELERY_IMPORTS setting.

# The debug_task example is a task that dumps its own request information. 
# Using the bind=True task option to easily refer to the current task instance.
#@celery_app.task(bind=True)
#def debug_task(self):
#    print('Request: {0!r}'.format(self.request))
