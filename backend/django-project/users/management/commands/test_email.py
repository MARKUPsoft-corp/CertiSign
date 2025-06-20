"""
Commande de test pour l'envoi d'email et de stockage de notifications
"""
import os
import sys
import logging
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from users.models import Organization
from users.utils import send_pending_account_notification
from users.notifications import save_notification, get_all_notifications

class Command(BaseCommand):
    help = "Test d'envoi d'email et de stockage de notifications"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            default='test@example.com',
            help='Adresse email de test (override)')
        parser.add_argument(
            '--type',
            choices=['direct', 'notification', 'all', 'view'],
            default='all',
            help='Type de test: direct, notification, all, ou view (afficher les notifications)')

    def handle(self, *args, **options):
        test_email = options['email']
        test_type = options['type']
        
        super_admin_email = getattr(settings, 'SUPER_ADMIN_EMAIL', 'no-super-admin@example.com')
        
        # Afficher un message sur la configuration mise à jour
        self.stdout.write(f"\n📫 CertiSign utilise maintenant un système de notifications locales")
        self.stdout.write(f"   Les notifications seront stockées dans le dossier local_notifications/")
        self.stdout.write(f"   Utilisez la commande ./manage.py view_notifications pour les consulter")
        
        # Si demande d'affichage des notifications
        if test_type == 'view':
            notifications = get_all_notifications()
            if not notifications:
                self.stdout.write(self.style.WARNING("\nAucune notification trouvée"))
            else:
                self.stdout.write(self.style.SUCCESS(f"\n{len(notifications)} notifications trouvées:"))
                for i, notif in enumerate(notifications[:5]):
                    self.stdout.write(f"\n{i+1}. {notif['subject']} (à: {notif['to']}) - {notif['timestamp']}")
            return
        
        # Test d'email direct (sauvegardé localement)
        if test_type in ['direct', 'all']:
            try:
                filepath = save_notification(
                    to_email=test_email,
                    subject='CertiSign Test Email Direct',
                    html_content='<p>Ceci est un <strong>test</strong> d\'envoi d\'email depuis CertiSign.</p>',
                    text_content='Ceci est un test d\'envoi d\'email depuis CertiSign.',
                    notification_type='test_direct'
                )
                self.stdout.write(self.style.SUCCESS(f"\n✅ Email direct sauvegardé avec succès dans: {filepath}"))
            except Exception as e:
                self.stdout.write(f"Erreur lors de la création de l'email direct : {str(e)}")
                self.stdout.write(self.style.ERROR(f"\n❌ Échec de création d'email direct"))
        
        # Test de notification
        if test_type in ['notification', 'all']:
            try:
                # Créer des objets temporaires pour le test
                User = get_user_model()
                test_user = User(
                    username="testadmin",
                    email=test_email,
                    first_name="Test",
                    last_name="Admin",
                    status="pending"
                )
                test_org = Organization(
                    name="Organisation Test",
                    registration_number="12345TEST",
                    address="123 Test Street",
                    email=test_email,
                    status="pending"
                )
                
                # Tester l'envoi de notification
                success = send_pending_account_notification(test_user, test_org, is_admin=True)
                
                if success:
                    self.stdout.write(self.style.SUCCESS(f"\n✅ Notification pour l'organisation créée avec succès"))
                else:
                    self.stdout.write(self.style.ERROR(f"\n❌ Échec de création de la notification"))
            except Exception as e:
                self.stdout.write(f"Erreur lors de la création de la notification : {str(e)}")
                self.stdout.write(self.style.ERROR(f"\n❌ Échec de création de la notification"))
        
        # Afficher la configuration actuelle
        self.stdout.write("\n--- Configuration notifications ---")
        self.stdout.write(f"SUPER_ADMIN_EMAIL: {super_admin_email}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Non défini')}")
        self.stdout.write(f"BASE_URL: {getattr(settings, 'BASE_URL', 'Non défini')}")
        self.stdout.write(f"NOTIFICATIONS_DIR: {os.path.join(settings.BASE_DIR, 'local_notifications')}")
        self.stdout.write("--------------------------------")
