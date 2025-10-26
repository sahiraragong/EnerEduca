import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from django.conf import settings  # ← importante para acceder a STATIC_ROOT

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'energeduca.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root=settings.STATIC_ROOT)
