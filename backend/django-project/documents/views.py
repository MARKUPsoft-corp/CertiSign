from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db import models
from django.core.files.base import ContentFile
from django.http import FileResponse
import uuid
import os
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from users.models import ActivityLog, CustomUser, Organization
from .models import DocumentActivity, DocumentSignature, DocumentQRPosition
from .serializers import DocumentActivitySerializer, DocumentSignatureSerializer, DocumentQRPositionSerializer
from .utils import get_sftp_file_response, check_sftp_connection
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
        
        # Utiliser l'utilitaire SFTP pour le téléchargement
        return get_sftp_file_response(
            file_to_download,
            filename=os.path.basename(file_to_download.name) if file_to_download.name else None
        )

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
        - Les administrateurs voient tous les documents de leur organisation
        - Les signataires voient tous les documents de leur organisation 
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
        
        if user.is_signer:
            # Signataire voit tous les documents de son organisation
            if user.organization:
                return DocumentQRPosition.objects.filter(organization=user.organization)
            else:
                # Signataire sans organisation ne voit rien
                return DocumentQRPosition.objects.none()
        
        # Collaborateur ne voit que ses propres documents
        return DocumentQRPosition.objects.filter(collaborator=user)
    
    def list(self, request, *args, **kwargs):
        """
        Surcharge de la méthode list pour s'assurer que le serializer est utilisé
        et que les URLs SFTP sont bien générées.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Surcharge de la méthode retrieve pour s'assurer que le serializer est utilisé
        et que les URLs SFTP sont bien générées.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def download_document(self, request, pk=None):
        """
        Télécharger le document original depuis SFTP
        """
        document = self.get_object()
        if not document.document_file:
            return Response(
                {"detail": "Aucun document disponible pour ce fichier."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Utiliser l'utilitaire SFTP pour le téléchargement
        import os
        return get_sftp_file_response(
            document.document_file,
            filename=os.path.basename(document.document_file.name) if document.document_file.name else None
        )
    
    @action(detail=True, methods=['get'])
    def download_generated_pdf(self, request, pk=None):
        """
        Télécharger le PDF généré avec QR code depuis SFTP
        """
        document = self.get_object()
        if not document.generated_pdf:
            return Response(
                {"detail": "Aucun PDF généré disponible pour ce document."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Utiliser l'utilitaire SFTP pour le téléchargement
        import os
        return get_sftp_file_response(
            document.generated_pdf,
            filename=os.path.basename(document.generated_pdf.name) if document.generated_pdf.name else None
        )
    
    @action(detail=True, methods=['get'])
    def download_signature_image(self, request, pk=None):
        """
        Télécharger l'image de signature depuis SFTP
        """
        document = self.get_object()
        if not document.signature_image:
            return Response(
                {"detail": "Aucune image de signature disponible pour ce document."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Utiliser l'utilitaire SFTP pour le téléchargement
        import os
        return get_sftp_file_response(
            document.signature_image,
            filename=os.path.basename(document.signature_image.name) if document.signature_image.name else None
        )
    
    def create(self, request, *args, **kwargs):
        """
        Création avec gestion détaillée des erreurs et gestion correcte des fichiers.
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
            
            # Gérer correctement les fichiers
            # Les fichiers sont déjà dans request.FILES, pas besoin de les traiter ici
            print("Fichiers reçus:", request.FILES)
            
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
        
        # L'utilisateur doit être un collaborateur pour accéder à cette vue
        if not user.is_collaborator:
            return Response(
                {"detail": "Accès non autorisé. Seuls les collaborateurs peuvent accéder à cette ressource."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        organization_id = request.query_params.get('organization_id')
        if not organization_id:
            return Response({"detail": "L'ID de l'organisation est requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({"detail": "Organisation non trouvée."}, status=status.HTTP_404_NOT_FOUND)

        # Vérifier si le collaborateur appartient bien à cette organisation
        if user.organization != organization:
            return Response({"detail": "Vous n'appartenez pas à cette organisation."}, status=status.HTTP_403_FORBIDDEN)
            
        # Filtrer les documents par l'ID de l'organisation
        queryset = DocumentQRPosition.objects.filter(organization_id=organization_id)

        # Répartir les documents par statut
        drafts = queryset.filter(status='draft')
        pending = queryset.filter(status='pending_signature')
        completed = queryset.filter(status='signed')
        
        # Créer les statistiques
        this_week = queryset.filter(created_at__gte=datetime.now() - timedelta(days=7)).count()
        this_month = queryset.filter(created_at__gte=datetime.now() - timedelta(days=30)).count()
        
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

    @action(detail=False, methods=['get'])
    def admin_dashboard(self, request):
        """
        Endpoint pour le tableau de bord administrateur.
        Filtre les données par l'organisation de l'admin connecté.
        """
        user = request.user
        
        # Vérifier que l'utilisateur a le rôle d'admin
        if not user.is_org_admin and not user.is_superadmin:
            return Response(
                {"error": "Vous n'avez pas les droits d'administrateur"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que l'utilisateur a une organisation (sauf superadmin)
        if not user.is_superadmin and not user.organization:
            return Response(
                {"error": "Vous n'êtes associé à aucune organisation"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filtrer par organisation
        if user.is_superadmin:
            # Superadmin peut voir toutes les organisations ou filtrer par organization_id
            organization_id = request.query_params.get('organization_id')
            if organization_id:
                try:
                    from users.models import Organization
                    organization = Organization.objects.get(id=organization_id)
                    documents = DocumentQRPosition.objects.filter(organization=organization)
                except Organization.DoesNotExist:
                    return Response(
                        {"error": "Organisation non trouvée"},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                documents = DocumentQRPosition.objects.all()
        else:
            # Admin d'organisation ne voit que les documents de son organisation
            documents = DocumentQRPosition.objects.filter(organization=user.organization)
        
        # Organiser par statut
        pending_documents = documents.filter(status='pending_signature')
        signed_documents = documents.filter(status='signed')
        draft_documents = documents.filter(status='draft')
        
        # Compter les documents par collaborateur
        collaborators_stats = {}
        for doc in documents:
            if doc.collaborator:
                username = doc.collaborator.username
                if username not in collaborators_stats:
                    collaborators_stats[username] = {
                        'id': doc.collaborator.id,
                        'username': username,
                        'email': doc.collaborator.email,
                        'total': 0,
                        'pending': 0,
                        'signed': 0,
                        'drafts': 0
                    }
                collaborators_stats[username]['total'] += 1
                if doc.status == 'pending_signature':
                    collaborators_stats[username]['pending'] += 1
                elif doc.status == 'signed':
                    collaborators_stats[username]['signed'] += 1
                elif doc.status == 'draft':
                    collaborators_stats[username]['drafts'] += 1
        
        # Statistiques générales
        total_documents = documents.count()
        this_week_docs = documents.filter(created_at__gte=datetime.now() - timedelta(days=7)).count()
        this_month_docs = documents.filter(created_at__gte=datetime.now() - timedelta(days=30)).count()
        
        # Sérialiser les documents les plus récents
        recent_documents = documents.order_by('-created_at')[:10]
        recent_documents_data = DocumentQRPositionSerializer(recent_documents, many=True, context={'request': request}).data
        
        return Response({
            'general_stats': {
                'total_documents': total_documents,
                'pending_signature': pending_documents.count(),
                'signed_documents': signed_documents.count(),
                'draft_documents': draft_documents.count(),
                'this_week': this_week_docs,
                'this_month': this_month_docs
            },
            'collaborators': list(collaborators_stats.values()),
            'recent_documents': recent_documents_data,
            'organization': user.organization.name if user.organization else "Toutes les organisations"
        })

    @action(detail=False, methods=['post'])
    def prepare_with_template(self, request):
        """
        Endpoint pour préparer un document en utilisant un template existant.
        
        Paramètres attendus :
        - document_file : Le fichier PDF à traiter
        - template_id : L'ID du template à utiliser
        - template_settings : Paramètres optionnels du template (JSON)
        - status : Statut du document ('draft' ou 'pending_signature')
        """
        try:
            user = request.user
            
            # Vérifier que l'utilisateur a le rôle de collaborateur
            if not user.is_collaborator and not user.is_admin and not user.is_superadmin:
                return Response(
                    {"error": "Seuls les collaborateurs peuvent préparer des documents"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Récupérer les paramètres
            document_file = request.FILES.get('document_file')
            generated_pdf_file = request.FILES.get('generated_pdf')  # Nouveau: PDF pré-généré avec QR/signatures
            template_id = request.data.get('template_id')
            template_settings = request.data.get('template_settings')
            doc_status = request.data.get('status', 'pending_signature')
            
            # Validation des paramètres
            if not document_file:
                return Response(
                    {"error": "Le fichier document est requis"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not template_id:
                return Response(
                    {"error": "L'ID du template est requis"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Récupérer le template
            try:
                from signature_templates.models import SignatureTemplate
                template = SignatureTemplate.objects.get(id=template_id)
                
                # Vérifier que l'utilisateur a accès à ce template
                if template.user != user and template.organization_name != (user.organization.name if user.organization else None):
                    return Response(
                        {"error": "Vous n'avez pas accès à ce template"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except SignatureTemplate.DoesNotExist:
                return Response(
                    {"error": "Template non trouvé"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Parser les template_settings si fournis
            parsed_settings = {}
            if template_settings:
                try:
                    import json
                    if isinstance(template_settings, str):
                        parsed_settings = json.loads(template_settings)
                    else:
                        parsed_settings = template_settings
                except json.JSONDecodeError:
                    return Response(
                        {"error": "Format JSON invalide pour template_settings"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Créer le document en copiant les paramètres du template
            document_data = {
                'document_file': document_file,
                'generated_pdf': generated_pdf_file,  # Peut être None si non fourni
                'document_name': document_file.name,
                'qr_x_position': template.qr_positions.get('default', {}).get('x', 50) if template.qr_positions else 50,
                'qr_y_position': template.qr_positions.get('default', {}).get('y', 50) if template.qr_positions else 50,
                'qr_size': template.qr_size,
                'qr_pages': 'all' if template.page_application == 'all' else ','.join(map(str, template.selected_pages)) if template.selected_pages else 'all',
                'qr_positions': template.qr_positions,
                'qr_mode': template.page_application,
                'signature_positions': template.signature_positions,
                'signature_size': template.signature_size,
                'signature_image': template.signature_image,
                'status': doc_status,
                'metadata': {
                    'template_used': {
                        'template_id': template.id,
                        'template_name': template.name,
                        'applied_at': datetime.now().isoformat()
                    },
                    'template_settings': parsed_settings
                }
            }
            
            # Créer l'instance du document
            document = DocumentQRPosition.objects.create(
                collaborator=user,
                organization=user.organization,
                **document_data
            )
            
            # Sérialiser la réponse
            serializer = DocumentQRPositionSerializer(document, context={'request': request})
            
            return Response(
                {
                    "message": "Document préparé avec succès en utilisant le template",
                    "document": serializer.data,
                    "template_used": {
                        "id": template.id,
                        "name": template.name
                    }
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            print(f"Erreur lors de la préparation avec template: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"Erreur serveur: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
