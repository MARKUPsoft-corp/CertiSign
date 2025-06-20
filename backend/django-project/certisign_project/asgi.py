"""
Configuration ASGI pour le projet CertiSign.

Ce module expose l'application ASGI utilisée par les serveurs web compatibles ASGI.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certisign_project.settings')

application = get_asgi_application() 