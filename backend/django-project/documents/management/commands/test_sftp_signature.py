"""
Commande de management pour tester l'accès aux images de signature SFTP.
"""
from django.core.management.base import BaseCommand
from django.urls import reverse
from documents.models import DocumentQRPosition
from documents.utils import get_sftp_file_response
from django.test import RequestFactory
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Teste l\'accès aux images de signature stockées sur SFTP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--document-id',
            type=str,
            help='ID du document à tester (optionnel)',
        )

    def handle(self, *args, **options):
        document_id = options.get('document_id')
        
        self.stdout.write(
            self.style.SUCCESS('=== TEST D\'ACCÈS AUX IMAGES DE SIGNATURE SFTP ===')
        )
        
        # Récupérer un document avec signature
        if document_id:
            try:
                document = DocumentQRPosition.objects.get(id=document_id)
                documents = [document]
            except DocumentQRPosition.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Document avec ID {document_id} non trouvé')
                )
                return
        else:
            # Récupérer le premier document avec signature
            documents = DocumentQRPosition.objects.filter(
                signature_image__isnull=False
            ).exclude(signature_image='')[:3]
            
            if not documents:
                self.stdout.write(
                    self.style.WARNING('Aucun document avec signature trouvé')
                )
                return
        
        # Créer un contexte de requête factice pour le sérialiseur
        factory = RequestFactory()
        request = factory.get('/')
        
        for document in documents:
            self.stdout.write(f'\n--- Document: {document.document_name} ---')
            self.stdout.write(f'ID: {document.id}')
            self.stdout.write(f'Signature image field: {document.signature_image}')
            
            if document.signature_image:
                # Tester l'URL SFTP générée par le sérialiseur
                from documents.serializers import DocumentQRPositionSerializer
                
                serializer = DocumentQRPositionSerializer(
                    document, 
                    context={'request': request}
                )
                
                signature_image_url = serializer.data.get('signature_image_url')
                self.stdout.write(f'URL SFTP générée: {signature_image_url}')
                
                # Tester l'accès direct au fichier SFTP
                try:
                    self.stdout.write('Test d\'accès direct au fichier SFTP...')
                    
                    # Utiliser l'utilitaire SFTP
                    response = get_sftp_file_response(
                        document.signature_image,
                        filename=os.path.basename(document.signature_image.name)
                    )
                    
                    if response:
                        self.stdout.write(
                            self.style.SUCCESS('✅ Accès SFTP réussi')
                        )
                        self.stdout.write(f'Type de contenu: {response.get("Content-Type", "Non spécifié")}')
                        self.stdout.write(f'Taille: {response.get("Content-Length", "Non spécifié")} bytes')
                    else:
                        self.stdout.write(
                            self.style.ERROR('❌ Échec de l\'accès SFTP')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Erreur lors de l\'accès SFTP: {e}')
                    )
                
                # Tester l'URL de téléchargement
                try:
                    download_url = reverse(
                        'document-qr-position-download-signature-image',
                        kwargs={'pk': document.id}
                    )
                    self.stdout.write(f'URL de téléchargement: {download_url}')
                    
                    # Construire l'URL absolue
                    from django.conf import settings
                    absolute_url = f"https://ppd.camgovca.cm{download_url}"
                    self.stdout.write(f'URL absolue: {absolute_url}')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Erreur lors de la génération de l\'URL: {e}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ Aucune image de signature pour ce document')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n=== FIN DU TEST ===')
        ) 