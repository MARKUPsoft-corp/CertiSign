"""
Configuration WSGI pour le projet CertiSign.

Ce module expose l'application WSGI utilisée par Django.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certisign_project.settings')

application = get_wsgi_application() 