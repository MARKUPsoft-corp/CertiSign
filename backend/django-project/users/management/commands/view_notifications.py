"""
Commande pour visualiser les notifications en attente
"""
from django.core.management.base import BaseCommand
from django.utils.termcolor import colored
import json
import os
import datetime
from pathlib import Path
from users.notifications import get_all_notifications

class Command(BaseCommand):
    help = "Affiche les notifications en attente de validation"

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            help="Type de notification à afficher ('pending_organization', 'pending_user', ou 'all')"
        )
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help="Nombre de notifications à afficher"
        )

    def handle(self, *args, **options):
        notification_type = options['type']
        count = options['count']
        
        # Récupérer toutes les notifications
        notifications = get_all_notifications()
        
        # Filtrer par type si nécessaire
        if notification_type != 'all':
            notifications = [n for n in notifications if n.get('type') == notification_type]
        
        # Limiter le nombre
        notifications = notifications[:count]
        
        if not notifications:
            self.stdout.write(self.style.WARNING("Aucune notification trouvée"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"=== {len(notifications)} notifications trouvées ==="))
        
        for i, notification in enumerate(notifications):
            self.stdout.write("━" * 80)
            self.stdout.write(self.style.SUCCESS(f"Notification #{i+1}:"))
            self.stdout.write(f"Date: {notification.get('timestamp')}")
            self.stdout.write(f"Type: {notification.get('type')}")
            self.stdout.write(f"À: {notification.get('to')}")
            self.stdout.write(f"De: {notification.get('from')}")
            self.stdout.write(f"Sujet: {colored(notification.get('subject'), 'yellow')}")
            self.stdout.write("")
            self.stdout.write(colored("Contenu (texte):", "green"))
            self.stdout.write(f"{notification.get('text_content')[:500]}...")
            self.stdout.write("")
            
            # Chemin du fichier
            self.stdout.write(f"Fichier: {notification.get('file_path')}")
            self.stdout.write("━" * 80)
            self.stdout.write("")
