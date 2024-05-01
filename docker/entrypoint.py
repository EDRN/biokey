# encoding: utf-8

'''Docker "entrypoint" for Gunicorn's WSGI server.'''

from django.core.wsgi import get_wsgi_application
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jpl.edrn.biokey.policy.settings.ops')
os.environ.setdefault('SECURE_COOKIES', 'True')
os.environ.setdefault('STATIC_ROOT', '/app/static')
os.environ.setdefault('MEDIA_ROOT', '/app/media')

application = get_wsgi_application()  # noqa

# The docker-compose context should provide these env vars:
#
# -   ALLOWED_HOSTS
# -   DATABASE_URL
# -   MEDIA_URL
# -   BASE_URL
# -   STATIC_URL
# -   SIGNING_KEY
# -   FORCE_SCRIPT_NAME
# -   LDAP_BIND_DN
# -   MQ_URL
# -   CACHE_URL
# -   RECAPTCHA_PRIVATE_KEY
# -   RECAPTCHA_PUBLIC_KEY
