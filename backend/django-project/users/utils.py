"""
Utilitaires pour le module users de CertiSign.
"""
import logging
import os
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

# Importer le module de notifications local
from .notifications import save_notification, send_pending_organization_notification

logger = logging.getLogger(__name__)



def get_client_ip(request):
    """
    Récupère l'adresse IP du client à partir de la requête.
    Utilisé pour la journalisation des actions.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def send_pending_account_notification(user_obj, org_obj=None, is_admin=False):
    """
    Envoie une notification au super administrateur lorsqu'un nouveau compte
    utilisateur ou une nouvelle organisation est en attente d'approbation.
    
    En mode développement, cette fonction sauvegarde la notification dans un fichier local
    plutôt que d'envoyer un email réel (en raison des restrictions SMTP).
    
    Args:
        user_obj: L'objet utilisateur en attente
        org_obj: L'objet organisation (optionnel, pour les administrateurs d'organisation)
        is_admin: Booléen indiquant si c'est un administrateur d'organisation
    
    Returns:
        bool: True si la notification a été créée avec succès
    """
    msg_type = "l'organisation" if is_admin else "l'utilisateur"
    print(f"\n📧 Création d'une notification pour {msg_type} {user_obj.username}")
    print(f"   → Destinataire: {settings.SUPER_ADMIN_EMAIL}")
    
    try:
        # Si c'est une notification d'organisation, utiliser la fonction spécialisée
        if is_admin and org_obj:
            return send_pending_organization_notification(user_obj, org_obj)
        
        # Pour les autres types (utilisateurs simples)
        subject = "CertiSign - Nouveau compte utilisateur en attente d'approbation"
        
        # Contexte pour le template d'email
        context = {
            'is_organization_admin': is_admin,
            'user': user_obj,
            'organization': org_obj,
            'admin_url': f"{settings.BASE_URL}/admin/users/{'organization' if is_admin else 'customuser'}/",
        }
        
        # Créer les versions HTML de l'email
        html_content = render_to_string('email/pending_account_notification.html', context)
        
        # Sauvegarder la notification (simulation d'envoi email)
        notification_type = "pending_organization" if is_admin else "pending_user"
        save_notification(
            to_email=settings.SUPER_ADMIN_EMAIL,
            subject=subject,
            html_content=html_content,
            notification_type=notification_type
        )
        
        # Journalisation
        entity_type = "l'organisation" if is_admin else "l'utilisateur"
        logger.info(f"Notification créée pour {entity_type} {user_obj.username} dans local_notifications/")
        return True
    
    except Exception as e:
        print(f"\n❌ ERREUR lors de la création de la notification: {e}")
        logger.error(f"Erreur lors de la création de la notification: {e}")
        return False
