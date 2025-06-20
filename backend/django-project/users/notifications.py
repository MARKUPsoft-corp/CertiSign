"""
Module de gestion des notifications locales pour CertiSign.
En environnement de développement, les emails sont stockés localement
dans un fichier pour simuler l'envoi réel.
"""
import os
import json
import datetime
from pathlib import Path
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Répertoire où stocker les notifications
NOTIFICATIONS_DIR = os.path.join(
    settings.BASE_DIR, 
    'local_notifications'
)

# Créer le répertoire si nécessaire
os.makedirs(NOTIFICATIONS_DIR, exist_ok=True)

def save_notification(to_email, subject, html_content, text_content=None, notification_type="general"):
    """
    Sauvegarde une notification dans un fichier JSON pour simulation d'envoi email
    en environnement de développement.
    
    Args:
        to_email (str): Adresse email du destinataire
        subject (str): Sujet de l'email
        html_content (str): Contenu HTML de l'email
        text_content (str, optional): Contenu texte de l'email
        notification_type (str): Type de notification (general, pending_org, etc.)
        
    Returns:
        str: Chemin du fichier de notification créé
    """
    if not text_content:
        text_content = strip_tags(html_content)
    
    # Générer un nom de fichier unique avec timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{notification_type}_{to_email.replace('@', '_at_')}.json"
    filepath = os.path.join(NOTIFICATIONS_DIR, filename)
    
    # Créer la structure de notification
    notification = {
        'timestamp': datetime.datetime.now().isoformat(),
        'to': to_email,
        'from': settings.DEFAULT_FROM_EMAIL,
        'subject': subject,
        'html_content': html_content,
        'text_content': text_content,
        'type': notification_type
    }
    
    # Sauvegarder dans un fichier JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(notification, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Notification sauvegardée dans {filepath}")
    print(f"   → Destinataire: {to_email}")
    print(f"   → Sujet: {subject}")
    
    return filepath

def get_all_notifications():
    """
    Récupère toutes les notifications sauvegardées
    
    Returns:
        list: Liste des notifications (dictionnaires)
    """
    notifications = []
    
    for file in Path(NOTIFICATIONS_DIR).glob('*.json'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                notification = json.load(f)
                notification['file_path'] = str(file)
                notifications.append(notification)
        except Exception as e:
            print(f"Erreur lors de la lecture de {file}: {e}")
    
    # Trier par timestamp décroissant (plus récent d'abord)
    return sorted(notifications, key=lambda x: x['timestamp'], reverse=True)

def send_pending_organization_notification(user_obj, org_obj):
    """
    Envoie (ou simule l'envoi) d'une notification pour une organisation en attente
    
    Args:
        user_obj: L'objet utilisateur administrateur
        org_obj: L'objet organisation
        
    Returns:
        bool: True si la notification a été créée avec succès
    """
    try:
        subject = "CertiSign - Nouvelle organisation en attente d'approbation"
        
        # Contexte pour le template
        context = {
            'is_organization_admin': True,
            'user': user_obj,
            'organization': org_obj,
            'admin_url': f"{settings.BASE_URL}/admin/users/organization/",
        }
        
        # Générer le contenu HTML
        html_content = render_to_string('email/pending_account_notification.html', context)
        
        # Sauvegarder la notification
        save_notification(
            to_email=settings.SUPER_ADMIN_EMAIL,
            subject=subject,
            html_content=html_content,
            notification_type="pending_organization"
        )
        
        return True
    
    except Exception as e:
        print(f"❌ Erreur lors de la création de la notification: {e}")
        return False
