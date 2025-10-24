"""
WSGI config for energeduca project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise  # importar WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energeduca.settings')

application = get_wsgi_application()
# Aquí se envuelve la aplicación con WhiteNoise para servir archivos estáticos
application = WhiteNoise(application, root=os.path.join(os.path.dirname(__file__), 'staticfiles'))
