"""
ASGI config for app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

"""
Django ASGI Entry Point with Environment Configuration
---------------------------------------------------

Key Responsibilities:
1. Sets the default Django settings module (app.settings.local) if not specified
2. Provides the ASGI application object for production servers
3. Maintains compatibility with both sync and async contexts

Environment Control Hierarchy:
----------------------------
The active settings module follows the same precedence as manage.py:
1. Explicit ENV variable (Highest priority)
   $ export DJANGO_SETTINGS_MODULE=app.settings.production
2. This setdefault() call (Fallback)

ASGI-Specific Notes:
-------------------
• This file is UNUSED in your current WSGI (Gunicorn/Nginx) setup
• Keep unchanged for future ASGI compatibility (Daphne, Uvicorn, etc.)
• Environment variables should match your WSGI configuration

Usage Guidance:
--------------
• Local Development (ASGI):
  $ daphne --settings=app.settings.local app.asgi:application

• Production Deployment:
  Same environment control as WSGI:
  $ export DJANGO_SETTINGS_MODULE=app.settings.production
  $ daphne app.asgi:application

Safety Considerations:
---------------------
• The setdefault() here must match your WSGI configuration
• Async-specific settings should be consistent with production.py
"""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.local")

application = get_asgi_application()
