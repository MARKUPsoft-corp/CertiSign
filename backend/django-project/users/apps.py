"""
Configuration de l'application utilisateurs.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class UsersConfig(AppConfig):
    """Configuration de l'application utilisateurs."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = _('Gestion des utilisateurs')
    
    def ready(self):
        """
        Méthode appelée quand l'application est prête.
        Import des signaux pour les enregistrer.
        """
        import users.signals 