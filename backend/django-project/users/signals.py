"""
Signaux pour l'application utilisateurs.
Ces signaux permettent d'automatiser certaines actions lors des opérations sur les utilisateurs.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import CustomUser, ActivityLog

@receiver(post_save, sender=CustomUser)
def log_user_creation(sender, instance, created, **kwargs):
    """
    Enregistre la création d'un nouvel utilisateur dans le journal d'activités.
    """
    if created:
        try:
            # Utilisateur qui a créé le compte (si disponible)
            creator = getattr(instance, '_creator', None)
            
            if creator:
                ActivityLog.objects.create(
                    user=creator,
                    action_type='status_change',
                    description=f"Création du compte utilisateur {instance.username}"
                )
        except Exception as e:
            # Log silencieux en cas d'erreur
            pass

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Enregistre la connexion d'un utilisateur dans le journal d'activités.
    """
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
    
    ActivityLog.objects.create(
        user=user,
        action_type='login',
        description=f"Connexion de l'utilisateur {user.username}",
        ip_address=ip_address
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Enregistre la déconnexion d'un utilisateur dans le journal d'activités.
    """
    if user:  # user can be None if the user is not authenticated
        ip_address = None
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
        
        ActivityLog.objects.create(
            user=user,
            action_type='logout',
            description=f"Déconnexion de l'utilisateur {user.username}",
            ip_address=ip_address
        ) 