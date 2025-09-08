from django.core.management.base import BaseCommand
from documents.models import DocumentQRPosition
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Nettoie les anciennes URLs /media/ et les remplace par des endpoints SFTP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui serait fait sans effectuer les changements',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Mode DRY-RUN - Aucun changement ne sera effectué'))
        
        # Récupérer tous les documents avec des URLs /media/
        documents_with_media_urls = DocumentQRPosition.objects.filter(
            document_file__contains='/media/'
        )
        
        self.stdout.write(f"Documents trouvés avec URLs /media/: {documents_with_media_urls.count()}")
        
        if not documents_with_media_urls.exists():
            self.stdout.write(self.style.SUCCESS('Aucun document avec des URLs /media/ trouvé'))
            return
        
        # Afficher les documents qui seraient modifiés
        for doc in documents_with_media_urls:
            self.stdout.write(f"Document ID: {doc.id}")
            self.stdout.write(f"  - Nom: {doc.document_name}")
            self.stdout.write(f"  - Ancienne URL: {doc.document_file}")
            self.stdout.write(f"  - Nouvelle URL: /api/documents/qr-positions/{doc.id}/download_document/")
            self.stdout.write("")
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY-RUN terminé - Utilisez --dry-run pour effectuer les changements'))
            return
        
        # Effectuer les modifications
        try:
            with transaction.atomic():
                updated_count = 0
                
                for doc in documents_with_media_urls:
                    # Extraire le nom du fichier de l'ancienne URL
                    old_url = str(doc.document_file)
                    if '/media/' in old_url:
                        # Remplacer l'URL par le chemin relatif du fichier
                        file_path = old_url.split('/media/')[-1]
                        doc.document_file = file_path
                        doc.save()
                        updated_count += 1
                        
                        self.stdout.write(f"Document {doc.id} mis à jour: {old_url} -> {file_path}")
                
                self.stdout.write(self.style.SUCCESS(f'{updated_count} documents mis à jour avec succès'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de la mise à jour: {e}'))
            raise 