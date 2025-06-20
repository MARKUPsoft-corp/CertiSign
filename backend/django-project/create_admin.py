import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certisign_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import Organization

User = get_user_model()

# Créer un super utilisateur
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User',
        role='superadmin',
        status='active'
    )
    print(f"Superutilisateur créé: {user.username}")
else:
    print("Un utilisateur avec ce nom existe déjà.")
