from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db import models
from django.core.files.base import ContentFile
from django.http import FileResponse
import uuid
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from users.models import ActivityLog, CustomUser, Organization
from .models import DocumentActivity, DocumentSignature, DocumentQRPosition
from .serializers import DocumentActivitySerializer, DocumentSignatureSerializer, DocumentQRPositionSerializer
from datetime import datetime, timedelta

class SignedDocumentViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les documents signés.
    Permet la consultation des documents signés et de leurs informations de signature.
    Toutes les actions sont journalisées automatiquement.
    """
    serializer_class = DocumentSignatureSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        user = self.request.user
        # Pour les superadmins et admins, montrer tous les documents
        if user.is_superadmin or user.is_org_admin:
            return DocumentSignature.objects.all()
        # Pour les utilisateurs normaux, montrer seulement leurs documents
        return DocumentSignature.objects.filter(owner=user)
    
    def perform_create(self, serializer):
        # Ce viewset ne gère pas directement la création des documents
        # Les documents sont créés via le processus de signature
        pass
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Enregistrer l'activité de consultation
        DocumentActivity.objects.create(
            document=instance,
            user=request.user,
            activity_type='viewed',
            description=f"Consultation du document signé: {instance.title or instance.document_id}",
            ip_address=self.get_client_ip()
        )
        
        return Response(serializer.data)
    
    def get_client_ip(self):
        """
        Récupérer l'adresse IP du client.
        """
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
        
    def perform_update(self, serializer):
        # Mettre à jour le document signé
        document = serializer.save()
        
        # Enregistrer l'activité de modification
        DocumentActivity.objects.create(
            document=document,
            user=self.request.user,
            activity_type='modified',
            description=f"Modification des métadonnées du document signé: {document.title or document.document_id}",
            ip_address=self.get_client_ip()
        )
        
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        document = self.get_object()
        
        # Enregistrer l'activité de téléchargement
        DocumentActivity.objects.create(
            document=document,
            user=request.user,
            activity_type='downloaded',
            description=f"Téléchargement du document signé: {document.title or document.document_id}",
            ip_address=self.get_client_ip()
        )
        
        # Déterminer le fichier à télécharger (original ou signé)
        file_to_download = document.signed_file if document.signed_file else document.original_file
        
        # Renvoyer le fichier comme réponse de téléchargement
        file_handle = file_to_download.open()
        response = FileResponse(file_handle, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_to_download.name}"'
        return response

    @action(detail=False, methods=['post'])
    def store_original(self, request):
        """
        Endpoint pour stocker le document original envoyé à l'API Gateway.
        Crée un nouveau DocumentSignature dans la base de données Django avec le fichier original.
        """
        try:
            # Vérifier la présence du fichier
            if 'document' not in request.FILES:
                return Response({"error": "Fichier manquant"}, status=status.HTTP_400_BAD_REQUEST)

            document_id = str(uuid.uuid4())
            
            # Créer un nouveau document de signature
            document = DocumentSignature(
                document_id=document_id,
                title=request.FILES['document'].name,
                owner=request.user,
                owner_username=request.user.username,
                status='pending_signature'
            )
            document.original_file = request.FILES['document']
            document.save()

            # Enregistrer l'activité
            DocumentActivity.objects.create(
                document=document,
                user=request.user,
                activity_type='created',
                description=f"Document envoyé pour signature: {document.title}",
                ip_address=self.get_client_ip()
            )

            return Response({
                "status": "success",
                "message": "Document original enregistré avec succès",
                "document_id": document.document_id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def store_signed(self, request):
        """
        Endpoint pour stocker le document signé reçu de l'API Gateway.
        Met à jour un DocumentSignature existant avec le fichier signé.
        """
        try:
            # Vérifier la présence des paramètres nécessaires
            if 'document_id' not in request.data:
                return Response({"error": "ID du document original manquant"}, status=status.HTTP_400_BAD_REQUEST)

            if 'signed_document' not in request.FILES:
                return Response({"error": "Document signé manquant"}, status=status.HTTP_400_BAD_REQUEST)

            # Récupérer le document existant
            try:
                document = DocumentSignature.objects.get(document_id=request.data['document_id'])
            except DocumentSignature.DoesNotExist:
                return Response({"error": "Document non trouvé"}, status=status.HTTP_404_NOT_FOUND)

            # Mettre à jour avec le document signé
            document.signed_file = request.FILES['signed_document']
            document.status = 'signed'
            document.signature_date = timezone.now()
            document.save()

            # Enregistrer l'activité
            DocumentActivity.objects.create(
                document=document,
                user=request.user,
                activity_type='signed',
                description=f"Document signé: {document.title or document.document_id}",
                ip_address=self.get_client_ip()
            )

            return Response({
                "status": "success",
                "message": "Document signé enregistré avec succès",
                "document_id": document.document_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=False, methods=['post'])
    def quick_sign(self, request):
        """
        Endpoint pour stocker à la fois le document original et le document signé en une seule requête.
        Utile lorsque le processus de signature est rapide ou géré localement.
        """
        try:
            # Vérifier la présence des fichiers
            if 'original_document' not in request.FILES or 'signed_document' not in request.FILES:
                return Response({"error": "Original ou document signé manquant"}, status=status.HTTP_400_BAD_REQUEST)

            document_id = str(uuid.uuid4())
            
            # Créer un nouveau document de signature
            document = DocumentSignature(
                document_id=document_id,
                title=request.data.get('title', request.FILES['original_document'].name),
                owner=request.user,
                owner_username=request.user.username,
                status='signed'
            )
            document.original_file = request.FILES['original_document']
            document.signed_file = request.FILES['signed_document']
            document.signature_date = timezone.now()
            document.save()

            # Enregistrer les activités
            DocumentActivity.objects.create(
                document=document,
                user=request.user,
                activity_type='created',
                description=f"Document créé: {document.title or document.document_id}",
                ip_address=self.get_client_ip()
            )

            DocumentActivity.objects.create(
                document=document,
                user=request.user,
                activity_type='signed',
                description=f"Document signé: {document.title or document.document_id}",
                ip_address=self.get_client_ip()
            )

            return Response({
                "status": "success",
                "message": "Documents original et signé enregistrés avec succès",
                "document_id": document.document_id
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DocumentActivityViewSet(viewsets.ModelViewSet):
    """
    API pour consulter et enregistrer les activités liées aux documents.
    """
    serializer_class = DocumentActivitySerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superadmin or user.is_org_admin:
            return DocumentActivity.objects.all()
        
        # Filtrer les activités liées aux documents possédés par l'utilisateur
        return DocumentActivity.objects.filter(
            models.Q(document__owner=user) | models.Q(user=user)
        ).distinct()
    
    @action(detail=False, methods=['post'])
    def record_activity(self, request):
        """
        Endpoint pour enregistrer une nouvelle activité utilisateur sur un document.
        Permet au frontend d'enregistrer toutes les interactions utilisateur.
        
        Paramètres attendus dans request.data:
        - document_id: UUID du document (obligatoire)
        - activity_type: Type d'activité (obligatoire, un des types définis dans le modèle)
        - description: Description de l'activité (optionnel)
        - metadata: Métadonnées supplémentaires au format JSON (optionnel)
        """
        try:
            # Vérifier les données requises
            document_id = request.data.get('document_id')
            activity_type = request.data.get('activity_type')
            
            if not document_id or not activity_type:
                return Response({
                    "error": "Les paramètres document_id et activity_type sont obligatoires"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier que le type d'activité est valide
            valid_types = [choice[0] for choice in DocumentActivity.ACTIVITY_TYPES]
            if activity_type not in valid_types:
                return Response({
                    "error": f"Type d'activité invalide. Valeurs possibles: {', '.join(valid_types)}"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Récupérer le document
            try:
                document = DocumentSignature.objects.get(document_id=document_id)
            except DocumentSignature.DoesNotExist:
                return Response({"error": "Document non trouvé"}, status=status.HTTP_404_NOT_FOUND)
            
            # Créer l'activité
            description = request.data.get('description', '')
            metadata = request.data.get('metadata', {})
            
            # Personnaliser la description si non fournie
            if not description:
                descriptions = {
                    'created': f"Création du document: {document.title or document.document_id}",
                    'viewed': f"Consultation du document: {document.title or document.document_id}",
                    'modified': f"Modification du document: {document.title or document.document_id}",
                    'signed': f"Signature du document: {document.title or document.document_id}",
                    'downloaded': f"Téléchargement du document: {document.title or document.document_id}",
                }
                description = descriptions.get(activity_type, f"Activité {activity_type} sur le document: {document.title or document.document_id}")
            
            # Obtenir l'adresse IP
            ip_address = self.get_client_ip(request)
            
            # Créer l'enregistrement d'activité
            activity = DocumentActivity.objects.create(
                document=document,
                user=request.user,
                activity_type=activity_type,
                description=description,
                ip_address=ip_address,
                metadata=metadata
            )
            
            # Journaliser également dans le journal d'activité général
            ActivityLog.objects.create(
                user=request.user,
                action_type=f'document_{activity_type}',
                description=description,
                ip_address=ip_address
            )
            
            serializer = self.get_serializer(activity)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_client_ip(self, request):
        """Récupère l'adresse IP du client."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=False, methods=['get'])
    def my_activities(self, request):
        # Récupérer seulement les activités de l'utilisateur actuel
        activities = DocumentActivity.objects.filter(user=request.user)
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

class DocumentQRPositionViewSet(viewsets.ModelViewSet):
    """
    API pour gérer le positionnement des QR codes sur les documents par les collaborateurs.
    """
    queryset = DocumentQRPosition.objects.all()
    serializer_class = DocumentQRPositionSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def get_queryset(self):
        """
        Filtrer les documents en fonction de l'utilisateur connecté.
        - Les administrateurs voient tous les documents
        - Les collaborateurs ne voient que leurs propres documents
        """
        user = self.request.user
        
        if user.is_superadmin or user.is_org_admin:
            if user.organization:
                # Admin d'organisation voit les documents de son organisation
                return DocumentQRPosition.objects.filter(organization=user.organization)
            else:
                # Super admin voit tout
                return DocumentQRPosition.objects.all()
        
        # Collaborateur ne voit que ses propres documents
        return DocumentQRPosition.objects.filter(collaborator=user)
    
    def create(self, request, *args, **kwargs):
        """
        Création avec gestion détaillée des erreurs pour faciliter le débogage.
        """
        try:
            # Afficher les données reçues pour débogage
            print("Données reçues:", request.data)
            
            # Imprimer toutes les clés présentes et leur type
            print("Clés et types:")
            for key, value in request.data.items():
                print(f"  - {key}: {type(value)}")
                if isinstance(value, str) and key not in ['document_name', 'status', 'qr_mode']:
                    print(f"    Valeur: {value[:100]}...")
            
            # Convertir les valeurs numériques en flottants
            data = request.data.copy()
            
            # Assurer que les valeurs sont des flottants
            try:
                if 'qr_x_position' in data:
                    data['qr_x_position'] = float(data['qr_x_position'])
                if 'qr_y_position' in data:
                    data['qr_y_position'] = float(data['qr_y_position'])
                # Nous ne convertissons plus qr_size car c'est maintenant une chaîne
            except (ValueError, TypeError) as e:
                return Response(
                    {"error": f"Valeur numérique invalide: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Créer le sérialiseur avec les données
            serializer = self.get_serializer(data=data)
            
            # Valider les données avec détails des erreurs
            if not serializer.is_valid():
                print("Erreurs de validation:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            # Ajouter l'utilisateur et l'organisation
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED, 
                headers=headers
            )
            
        except Exception as e:
            print(f"Erreur lors de la création: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"Erreur serveur: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def perform_create(self, serializer):
        """
        Lors de la création, associer automatiquement le collaborateur et l'organisation.
        """
        user = self.request.user
        
        # Vérifier que l'utilisateur a bien le rôle de collaborateur
        if not user.is_collaborator and not user.is_admin and not user.is_superadmin:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seuls les collaborateurs peuvent préparer des documents")
        
        # Enregistrer avec les informations du collaborateur
        serializer.save(
            collaborator=user,
            organization=user.organization
        )
    
    @action(detail=False, methods=['get'])
    def by_collaborator(self, request):
        """
        Endpoint pour récupérer tous les documents préparés par le collaborateur connecté.
        """
        user = request.user
        documents = DocumentQRPosition.objects.filter(collaborator=user)
        
        # Organiser par statut
        drafts = documents.filter(status='draft')
        pending = documents.filter(status='pending_signature')
        completed = documents.filter(status='signed')
        
        # Créer les statistiques
        this_week = documents.filter(created_at__gte=datetime.now() - timedelta(days=7)).count()
        this_month = documents.filter(created_at__gte=datetime.now() - timedelta(days=30)).count()
        
        # Sérialiser les données
        drafts_data = DocumentQRPositionSerializer(drafts, many=True, context={'request': request}).data
        pending_data = DocumentQRPositionSerializer(pending, many=True, context={'request': request}).data
        completed_data = DocumentQRPositionSerializer(completed, many=True, context={'request': request}).data
        
        return Response({
            'drafts': drafts_data,
            'pending': pending_data,
            'completed': completed_data,
            'stats': {
                'this_week': this_week,
                'this_month': this_month,
                'avg_time': '2j'  # À remplacer par un calcul réel
            }
        })

    @action(detail=False, methods=['get'])
    def pending_for_signer(self, request):
        """
        Récupère les documents en attente de signature pour un signataire.
        Filtre sur l'organisation du signataire connecté.
        """
        user = request.user
        
        # Vérifier que l'utilisateur a le rôle de signataire ou collaborateur
        if not user.is_signer and not user.is_collaborator and not user.is_admin and not user.is_superadmin:
            return Response(
                {"error": "Vous n'avez pas les droits de signataire ou collaborateur"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que l'utilisateur a une organisation
        if not user.organization:
            return Response(
                {"error": "Vous n'êtes associé à aucune organisation"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer les documents en attente de signature pour cette organisation
        documents = DocumentQRPosition.objects.filter(
            organization=user.organization,
            status='pending_signature'
        ).order_by('-created_at')
        
        # Sérialiser les données
        serializer = self.get_serializer(documents, many=True)
        
        # Ajouter des informations complémentaires pour l'affichage
        documents_data = []
        for doc in serializer.data:
            # Vérifier l'urgence basée sur la date de création (plus de 3 jours = urgent)
            created_at = datetime.strptime(doc['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            is_urgent = (datetime.now() - created_at).days >= 3
            
            # Ajouter des métadonnées d'affichage
            document_data = {
                **doc,
                'is_urgent': is_urgent,
                'preparedBy': doc['collaborator_username'] or 'Collaborateur',
                'assignedAt': doc['created_at']
            }
            documents_data.append(document_data)
        
        # Ajouter des statistiques
        stats = {
            'thisWeek': DocumentQRPosition.objects.filter(
                organization=user.organization,
                status='signed',
                updated_at__gte=datetime.now() - timedelta(days=7)
            ).count(),
            'total': DocumentQRPosition.objects.filter(
                organization=user.organization,
                status='signed'
            ).count(),
            'avgTime': '1j'  # Valeur statique pour l'instant
        }
        
        return Response({
            'pending_documents': documents_data,
            'stats': stats
        })
