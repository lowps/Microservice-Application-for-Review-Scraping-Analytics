"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# app.settings -> settings.local
# if in production environment or venv & you want to do production settings then
# <export DJANGO_SETTINGS_MODULE=settings.production> and update
# settings.local -> settings.production

"""
The wsgi.py is the entry point when deploying your Django app on a WSGI server (e.g., Gunicorn, uWSGI).
It needs the correct DJANGO_SETTINGS_MODULE environment variable set so Django knows which settings to use.
If you leave it at 'app.settings.local', your production server will load local/dev settings instead of production settings, 
which may cause misconfiguration (e.g., debug mode on, wrong DB settings, etc.).
"""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.local")

application = get_wsgi_application()
