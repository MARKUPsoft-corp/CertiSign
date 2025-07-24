"""
Vues dédiées à la gestion des signatures de documents.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, parser_classes, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import models
import uuid
import json
import logging

from .models import DocumentSignature, DocumentActivity
from .serializers import DocumentSignatureSerializer
from users.models import ActivityLog
from rest_framework.decorators import authentication_classes, permission_classes

# Configuration du logging
logger = logging.getLogger(__name__)

# Clé secrète pour les microservices - pour l'authentification simple
MICROSERVICE_API_KEY = "certisign_microservice_key_2025"

class DocumentSignatureViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les signatures de documents.
    Permet de stocker et récupérer les informations de signature.
    """
    queryset = DocumentSignature.objects.all()
    serializer_class = DocumentSignatureSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [permissions.IsAuthenticated]  # Autoriser les utilisateurs authentifiés
    lookup_field = 'document_id'  # Utiliser document_id au lieu de pk
    
    def get_queryset(self):
        user = self.request.user
        queryset = DocumentSignature.objects.all()
        
        # Filtrage par organisation si spécifié dans les paramètres de requête
        organization_id = self.request.query_params.get('organization_id')
        
        # Pour les utilisateurs non authentifiés, aucune signature n'est visible
        if not user.is_authenticated:
            return DocumentSignature.objects.none()
        
        # Pour les superadmins, montrer toutes les signatures (avec filtres éventuels)
        if user.is_superadmin:
            if organization_id:
                return queryset.filter(organization_id=organization_id)
            return queryset
        
        # Pour tous les autres utilisateurs (admin org, collaborateur, signataire),
        # filtrer par leur organisation
        if user.organization:
            # Si un organization_id est spécifié, vérifier qu'il correspond à l'organisation de l'utilisateur
            if organization_id:
                if str(user.organization.id) == organization_id:
                    return queryset.filter(organization=user.organization)
                else:
                    # L'utilisateur demande des données d'une autre organisation
                    return DocumentSignature.objects.none()
            else:
                # Sans filtre spécifique, montrer les documents de l'organisation de l'utilisateur
                return queryset.filter(organization=user.organization)
        
        # Si l'utilisateur n'a pas d'organisation, montrer ses propres documents
        # (utilisateurs individuels sans organisation)
        if organization_id:
            # Si un organization_id est demandé mais l'utilisateur n'a pas d'organisation, 
            # ne rien montrer
            return DocumentSignature.objects.none()
        else:
            # Montrer SEULEMENT les documents dont cet utilisateur est propriétaire
            # ET qui n'appartiennent à aucune organisation (sécurité)
            return queryset.filter(
                models.Q(owner=user) & models.Q(organization__isnull=True)
            )
    
    @action(detail=True, methods=['get'])
    def download(self, request, document_id=None):
        """
        Télécharge le document signé ou original
        """
        from django.http import FileResponse
        
        document = self.get_object()
        
        # Enregistrer l'activité de téléchargement
        DocumentActivity.objects.create(
            document=document,
            user=request.user if request.user.is_authenticated else None,
            activity_type='downloaded',
            description=f"Téléchargement du document signé: {document.title or document.document_id}"
        )
        
        # Déterminer le fichier à télécharger (original ou signé)
        file_to_download = document.signed_file if document.signed_file else document.original_file
        
        if not file_to_download:
            return Response({"error": "Aucun fichier disponible pour ce document"}, status=status.HTTP_404_NOT_FOUND)
        
        # Renvoyer le fichier comme réponse de téléchargement
        file_handle = file_to_download.open()
        response = FileResponse(file_handle, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_to_download.name}"'
        return response
        
    @action(detail=True, methods=['get'])
    def download_original(self, request, document_id=None):
        """
        Télécharge spécifiquement le document original, même si une version signée existe
        """
        from django.http import FileResponse
        
        document = self.get_object()
        
        # Enregistrer l'activité de téléchargement du document original
        DocumentActivity.objects.create(
            document=document,
            user=request.user if request.user.is_authenticated else None,
            activity_type='downloaded',
            description=f"Téléchargement du document original: {document.title or document.document_id}"
        )
        
        # Utiliser explicitement le fichier original, jamais le fichier signé
        file_to_download = document.original_file
        
        if not file_to_download:
            return Response({"error": "Aucun fichier original disponible pour ce document"}, status=status.HTTP_404_NOT_FOUND)
        
        # Renvoyer le fichier comme réponse de téléchargement
        file_handle = file_to_download.open()
        response = FileResponse(file_handle, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="original_{file_to_download.name}"'
        return response
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def store_signature(self, request):
        """
        Stocke une nouvelle signature de document.
        Cette action est appelée par le microservice de signature.
        Exige une authentification JWT.
        """
        try:
            # Vérifier les données requises
            required_fields = ['document_id', 'original_hash', 'signature', 'public_key_pem']
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {"error": f"Champ requis manquant: {field}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Vérifier la présence des fichiers
            if 'original_file' not in request.FILES or 'signed_file' not in request.FILES:
                return Response(
                    {"error": "Les fichiers original_file et signed_file sont requis"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Traitement des paramètres
            document_id = request.data.get('document_id')
            if not document_id:
                document_id = str(uuid.uuid4())
            
            original_hash = request.data.get('original_hash')
            signature = request.data.get('signature')
            public_key_pem = request.data.get('public_key_pem')
            title = request.data.get('title')
            
            # Récupérer le propriétaire si un ID est fourni
            owner = None
            owner_id = request.data.get('owner_id')
            if owner_id:
                User = get_user_model()
                try:
                    owner = User.objects.get(id=owner_id)
                except User.DoesNotExist:
                    logger.warning(f"Propriétaire avec ID {owner_id} non trouvé")
            elif request.user.is_authenticated:
                owner = request.user
            
            # Récupérer l'organisation et le rôle du signataire
            organization = None
            organization_id = request.data.get('organization_id')
            if organization_id:
                from users.models import Organization
                try:
                    organization = Organization.objects.get(id=organization_id)
                except Organization.DoesNotExist:
                    logger.warning(f"Organisation avec ID {organization_id} non trouvée")
            elif owner and owner.organization:
                organization = owner.organization
            
            # Récupérer le rôle du signataire
            signer_role = request.data.get('signer_role')
            if not signer_role and owner:
                signer_role = owner.position or owner.get_role_display()
            
            # Récupérer les fichiers
            original_file = request.FILES['original_file']
            signed_file = request.FILES['signed_file']
            
            # Vérifier si une signature avec cet ID existe déjà
            try:
                existing_signature = DocumentSignature.objects.get(document_id=document_id)
                # Si elle existe, envoyer une erreur
                return Response(
                    {"error": f"Une signature avec l'ID {document_id} existe déjà"},
                    status=status.HTTP_409_CONFLICT
                )
            except DocumentSignature.DoesNotExist:
                pass
            
            # Créer la signature de document
            document_signature = DocumentSignature(
                document_id=document_id,
                original_hash=original_hash,
                signature=signature,
                public_key_pem=public_key_pem,
                title=title,
                owner=owner,
                organization=organization,
                signer_role=signer_role
            )
            
            # Associer les fichiers
            document_signature.original_file = original_file
            document_signature.signed_file = signed_file
            
            # Enregistrer la signature
            document_signature.save()
            
            # Si l'utilisateur est authentifié, enregistrer l'activité
            if owner:
                ActivityLog.objects.create(
                    user=owner,
                    action_type='sign',
                    description=f"Signature du document: {title or document_id}"
                )
            
            # Renvoyer la réponse
            return Response({
                "status": "success",
                "message": "Signature stockée avec succès",
                "document_id": document_id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Erreur lors du stockage de la signature: {str(e)}")
            return Response(
                {"error": f"Erreur lors du stockage de la signature: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        """
        Vérifie la signature d'un document en récupérant les informations stockées.
        """
        try:
            # Récupérer la signature par son ID (document_id)
            signature = self.get_object()
            
            # Informations enrichies sur le signataire (si disponible)
            signer_info = {}
            if signature.owner:
                user = signature.owner
                signer_info = {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "full_name": f"{user.first_name} {user.last_name}".strip() or user.username,
                    "role": user.get_role_display(),
                    "organization": user.organization.name if hasattr(user, 'organization') and user.organization else "",
                    "position": user.position if hasattr(user, 'position') else "",
                    "signature_timestamp": signature.created_at.isoformat(),
                    "signature_date": signature.created_at.strftime("%d/%m/%Y %H:%M"),
                    "is_verified": True  # L'utilisateur est authentifié dans le système
                }
            
            # Ajouter les informations spécifiques de la signature
            if signature.organization:
                signer_info["organization_id"] = str(signature.organization.id)
                signer_info["organization_name"] = signature.organization.name
            
            if signature.signer_role:
                signer_info["signer_role"] = signature.signer_role
            
            # Renvoyer les données de signature complètes
            return Response({
                "document_id": str(signature.document_id),
                "original_hash": signature.original_hash,
                "signature": signature.signature,
                "public_key_pem": signature.public_key_pem,
                "created_at": signature.created_at.isoformat(),
                "title": signature.title,
                "signer_info": signer_info
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la signature: {str(e)}")
            return Response(
                {"error": f"Erreur lors de la récupération: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_signature_by_id(request, document_id):
    """
    Point d'entrée public pour récupérer les informations de signature par l'ID du document.
    Cette API est utilisée par le microservice de vérification.
    """
    try:
        # Convertir document_id en UUID si nécessaire
        try:
            # Si c'est déjà un UUID, cela fonctionnera directement
            uuid_id = uuid.UUID(document_id)
        except (ValueError, TypeError):
            # Si la conversion échoue, retournons une erreur explicite
            return Response(
                {"error": f"Format d'identifiant de document invalide: {document_id}. Un UUID est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer la signature par son document_id
        signature = get_object_or_404(DocumentSignature, document_id=uuid_id)
        
        # Informations enrichies sur le signataire (si disponible)
        signer_info = {}
        if signature.owner:
            user = signature.owner
            signer_info = {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": f"{user.first_name} {user.last_name}".strip() or user.username,
                "role": user.get_role_display(),
                "organization": user.organization.name if hasattr(user, 'organization') and user.organization else "",
                "position": user.position if hasattr(user, 'position') else "",
                "signature_timestamp": signature.created_at.isoformat(),
                "signature_date": signature.created_at.strftime("%d/%m/%Y %H:%M"),
                "is_verified": True  # L'utilisateur est authentifié dans le système
            }
        
        # Renvoyer les données de signature
        return Response({
            "document_id": str(signature.document_id),
            "original_hash": signature.original_hash,
            "signature": signature.signature,
            "public_key_pem": signature.public_key_pem,
            "created_at": signature.created_at.isoformat(),
            "title": signature.title,
            "signer_info": signer_info
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la signature {document_id}: {str(e)}")
        return Response(
            {"error": f"Erreur lors de la récupération: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@require_POST
def standard_store_signature_public(request):
    """
    Endpoint public pour stocker une signature de document sans aucun middleware d'authentification.
    Vue Django standard (pas REST Framework) pour éviter les middleware d'authentification JWT.
    Utilise une simple clé API pour l'authentification entre microservices.
    
    Cette approche simplifie la communication entre les microservices FastAPI et Django.
    """
    try:
        # Déboguer tous les en-têtes et params reçus dans la requête
        logger.info("En-têtes reçus dans la requête standard:")
        for header_name, header_value in request.headers.items():
            logger.info(f"  {header_name}: {header_value}")
        
        # La clé API peut être dans un en-tête ou un paramètre de requête
        header_api_key = request.headers.get('X-Api-Key') or request.META.get('HTTP_X_API_KEY')
        query_api_key = request.GET.get('api_key')
        
        api_key = header_api_key or query_api_key
        
        logger.info(f"Clé API dans l'en-tête: {header_api_key}")
        logger.info(f"Clé API dans le paramètre: {query_api_key}")
        logger.info(f"Clé API attendue: {MICROSERVICE_API_KEY}")
        
        # Vérifier la clé API
        if not api_key:
            logger.warning("Aucune clé API trouvée dans les en-têtes ou paramètres")
            return JsonResponse({"error": "Clé API manquante"}, status=401)
        
        if api_key != MICROSERVICE_API_KEY:
            logger.warning(f"Clé API invalide reçue: {api_key}")
            return JsonResponse({"error": "Clé API invalide"}, status=401)
        
        # Vérifier les données requises
        required_fields = ['document_id', 'original_hash', 'signature', 'public_key_pem']
        for field in required_fields:
            if field not in request.POST:
                return JsonResponse({"error": f"Champ requis manquant: {field}"}, status=400)
        
        # Vérifier la présence des fichiers
        if 'original_file' not in request.FILES or 'signed_file' not in request.FILES:
            return JsonResponse({"error": "Les fichiers original_file et signed_file sont requis"}, status=400)
        
        # Traitement des paramètres
        document_id = request.POST.get('document_id')
        if not document_id:
            document_id = str(uuid.uuid4())
        
        logger.info(f"Traitement de la signature avec l'ID: {document_id}")
        
        original_hash = request.POST.get('original_hash')
        signature = request.POST.get('signature')
        public_key_pem = request.POST.get('public_key_pem')
        title = request.POST.get('title')
        
        # Récupérer le propriétaire si un ID est fourni
        owner = None
        owner_id = request.POST.get('owner_id')
        
        # Journaliser l'owner_id reçu
        logger.info(f"Owner ID reçu: {owner_id}, type: {type(owner_id)}")
        
        # Si l'owner_id est la chaîne littérale 'string', c'est une valeur par défaut invalide
        if owner_id and owner_id.lower() != 'string':
            # Essayons de convertir l'owner_id en nombre entier
            try:
                owner_id_int = int(owner_id)
                User = get_user_model()
                try:
                    owner = User.objects.get(id=owner_id_int)
                    logger.info(f"Propriétaire trouvé: {owner.username}")
                except User.DoesNotExist:
                    logger.warning(f"Propriétaire avec ID {owner_id_int} non trouvé")
            except (ValueError, TypeError):
                logger.warning(f"Owner ID invalide (non numérique): {owner_id}")
        else:
            logger.info("Aucun owner_id valide fourni, signature sans propriétaire")
            
        # Récupérer les informations d'organisation et de signataire
        organization_id = request.POST.get('organization_id')
        organization_name = request.POST.get('organization_name')
        signer_role = request.POST.get('signer_role')
        signer_name = request.POST.get('signer_name')
        
        # 🆕 TRAITEMENT DES SIGNATURES ÉPHÉMÈRES
        signature_type = 'permanent'  # Valeur par défaut
        expiration_date = None
        
        # Extraire les informations de type de signature depuis les métadonnées
        metadata_str = request.POST.get('metadata') or request.POST.get('user_metadata')
        if metadata_str:
            try:
                import json
                metadata_dict = json.loads(metadata_str)
                logger.info(f"Métadonnées parsées: {list(metadata_dict.keys())}")
                
                # Extraire le type de signature
                if 'signature_type' in metadata_dict:
                    signature_type = metadata_dict['signature_type']
                    logger.info(f"Type de signature extrait: {signature_type}")
                
                # Extraire la date d'expiration pour les signatures éphémères
                if signature_type == 'ephemeral' and 'expiration_date' in metadata_dict:
                    from django.utils.dateparse import parse_datetime
                    expiration_date = parse_datetime(metadata_dict['expiration_date'])
                    logger.info(f"Date d'expiration extraite: {expiration_date}")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Erreur lors du parsing des métadonnées: {str(e)}")
                # Continuer avec les valeurs par défaut
        
        logger.info(f"Configuration signature - Type: {signature_type}, Expiration: {expiration_date}")
        
        # Récupérer l'organisation si un ID est fourni
        organization = None
        if organization_id:
            from users.models import Organization
            try:
                organization = Organization.objects.get(id=organization_id)
                # Si organization_name n'est pas fourni, utiliser le nom de l'organisation trouvée
                if not organization_name:
                    organization_name = organization.name
            except Organization.DoesNotExist:
                logger.warning(f"Organisation avec ID {organization_id} non trouvée")
        
        logger.info(f"Informations de signature - Organisation: {organization_name}, Signataire: {signer_name}, Rôle: {signer_role}")
        
        # Récupérer les fichiers
        original_file = request.FILES['original_file']
        signed_file = request.FILES['signed_file']
        
        # Vérifier si une signature avec cet ID existe déjà
        try:
            existing_signature = DocumentSignature.objects.get(document_id=document_id)
            # Si elle existe, envoyer une erreur
            return JsonResponse(
                {"error": f"Une signature avec l'ID {document_id} existe déjà"},
                status=409
            )
        except DocumentSignature.DoesNotExist:
            pass
        
        # Créer la signature de document
        document_signature = DocumentSignature(
            document_id=document_id,
            original_hash=original_hash,
            signature=signature,
            public_key_pem=public_key_pem,
            title=title,
            owner=owner,
            organization=organization,
            organization_name=organization_name,
            signer_role=signer_role,
            signer_name=signer_name,
            # 🆕 NOUVEAUX CHAMPS POUR SIGNATURES ÉPHÉMÈRES
            signature_type=signature_type,
            expiration_date=expiration_date
        )
        
        # Associer les fichiers
        document_signature.original_file = original_file
        document_signature.signed_file = signed_file
        
        # Enregistrer la signature
        document_signature.save()
        
        # Si l'utilisateur est authentifié, enregistrer l'activité
        if owner:
            ActivityLog.objects.create(
                user=owner,
                action_type='sign',
                description=f"Signature du document: {title or document_id}"
            )
        
        # Journaliser l'opération
        logger.info(f"Signature {document_id} stockée avec succès via l'API standard")
        
        # Renvoyer la réponse
        return JsonResponse({
            "status": "success",
            "message": "Signature stockée avec succès",
            "document_id": document_id
        }, status=201)
    
    except Exception as e:
        logger.error(f"Erreur lors du stockage de la signature (vue standard): {str(e)}")
        return JsonResponse({"error": f"Erreur lors du stockage: {str(e)}"}, status=500)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([permissions.AllowAny])  # Permet l'accès sans authentification
def store_signature_public(request):
    """
    Endpoint public pour stocker une signature de document sans authentification JWT.
    Utilise une simple clé API pour l'authentification entre microservices.
    
    Cette approche simplifie la communication entre les microservices FastAPI et Django.
    """


@csrf_exempt
def standard_get_signature_public(request):
    """
    Endpoint public pour récupérer les informations de signature par l'ID du document sans aucun middleware d'authentification.
    Vue Django standard (pas REST Framework) pour éviter les middleware d'authentification JWT.
    Utilise une simple clé API pour l'authentification entre microservices.
    
    Cette approche simplifie la communication entre les microservices FastAPI et Django pour la vérification.
    """
    logger.info("Accès à l'endpoint public de récupération de signature")
    
    # Vérifier si la méthode est GET
    if request.method != 'GET':
        return HttpResponseBadRequest("Méthode non autorisée. Utilisez GET.")
    
    # Vérifier la clé API
    api_key = request.GET.get('api_key')
    if not api_key or api_key != MICROSERVICE_API_KEY:
        logger.warning(f"Tentative d'accès avec une clé API invalide: {api_key}")
        return JsonResponse(
            {"error": "Accès non autorisé. Clé API invalide."}, 
            status=401
        )
    
    # Récupérer l'ID du document depuis les paramètres GET
    document_id = request.GET.get('document_id')
    if not document_id:
        return JsonResponse(
            {"error": "ID de document manquant dans la requête."}, 
            status=400
        )
        
    # Nettoyer l'ID du document (supprimer les espaces blancs)
    document_id = document_id.strip()
    logger.info(f"ID du document nettoyé: '{document_id}'")
    
    try:
        # Convertir document_id en UUID si nécessaire
        try:
            # Si c'est déjà un UUID, cela fonctionnera directement
            uuid_id = uuid.UUID(document_id)
        except (ValueError, TypeError):
            # Si la conversion échoue, retournons une erreur explicite
            return JsonResponse(
                {"error": f"Format d'identifiant de document invalide: {document_id}. Un UUID est requis."},
                status=400
            )
        
        # Récupérer la signature par son document_id
        try:
            signature = DocumentSignature.objects.get(document_id=uuid_id)
        except DocumentSignature.DoesNotExist:
            return JsonResponse(
                {"error": f"Aucune signature trouvée pour le document ID: {document_id}"},
                status=404
            )
        
        # Informations sur le signataire (si disponible)
        signer_info = {}
        if signature.owner:
            user = signature.owner
            signer_info = {
                "username": user.username,
                "email": user.email,
                "full_name": f"{user.first_name} {user.last_name}".strip() or user.username,
                "role": user.get_role_display()
            }
        
        # Récupérer l'URL du fichier original
        original_file_url = None
        original_file_path = None
        if signature.original_file:
            try:
                original_file_url = signature.original_file.url
                original_file_path = signature.original_file.path
                logger.info(f"URL du fichier original trouvée: {original_file_url}")
                logger.info(f"Chemin du fichier original: {original_file_path}")
            except Exception as e:
                logger.warning(f"Impossible de récupérer l'URL du fichier original: {str(e)}")
        
        # 🎯 AJOUT : Récupérer l'URL du fichier SIGNÉ
        signed_file_url = None
        signed_file_path = None
        if signature.signed_file:
            try:
                signed_file_url = signature.signed_file.url
                signed_file_path = signature.signed_file.path
                logger.info(f"✅ URL du fichier SIGNÉ trouvée: {signed_file_url}")
                logger.info(f"✅ Chemin du fichier SIGNÉ: {signed_file_path}")
            except Exception as e:
                logger.warning(f"❌ Impossible de récupérer l'URL du fichier signé: {str(e)}")
        else:
            logger.warning(f"⚠️ Aucun fichier signé trouvé pour le document {document_id}")
        
        # Renvoyer les données de signature avec le fichier signé
        return JsonResponse({
            "document_id": str(signature.document_id),
            "original_hash": signature.original_hash,
            "signature": signature.signature,
            "public_key_pem": signature.public_key_pem,
            "created_at": signature.created_at.isoformat(),
            "title": signature.title,
            "signer_info": signer_info,
            "original_file_url": original_file_url,
            "original_file_path": original_file_path,
            "signed_file_url": signed_file_url,  # 🎯 NOUVEAU !
            "signed_file_path": signed_file_path  # 🎯 NOUVEAU !
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la signature {document_id}: {str(e)}")
        return JsonResponse(
            {"error": f"Erreur lors de la récupération: {str(e)}"},
            status=500
        )


def store_signature_public(request):
    """
    Endpoint public pour stocker une signature de document sans authentification JWT.
    Utilise une simple clé API pour l'authentification entre microservices.
    
    Cette approche simplifie la communication entre les microservices FastAPI et Django.
    """
    # Déboguer tous les en-têtes et params reçus dans la requête
    logger.info("En-têtes reçus dans la requête:")
    for header_name, header_value in request.headers.items():
        logger.info(f"  {header_name}: {header_value}")
        
    logger.info("Paramètres de requête reçus:")
    for param_name, param_value in request.GET.items():
        logger.info(f"  {param_name}: {param_value}")
    
    # Vérifier la clé API dans les en-têtes ET dans les paramètres de requête
    header_api_key = request.headers.get('X-Api-Key') or request.headers.get('x-api-key') or request.META.get('HTTP_X_API_KEY')
    query_api_key = request.GET.get('api_key')
    
    api_key = header_api_key or query_api_key
    
    logger.info(f"Clé API dans l'en-tête: {header_api_key}")
    logger.info(f"Clé API dans le paramètre: {query_api_key}")
    logger.info(f"Clé API attendue: {MICROSERVICE_API_KEY}")
    
    if not api_key:
        logger.warning("Aucune clé API trouvée dans les en-têtes ou paramètres")
        return Response(
            {"error": "Clé API manquante"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if api_key != MICROSERVICE_API_KEY:
        logger.warning(f"Clé API invalide reçue: {api_key}")
        return Response(
            {"error": "Clé API invalide"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Vérifier les données requises
        required_fields = ['document_id', 'original_hash', 'signature', 'public_key_pem']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {"error": f"Champ requis manquant: {field}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Vérifier la présence des fichiers
        if 'original_file' not in request.FILES or 'signed_file' not in request.FILES:
            return Response(
                {"error": "Les fichiers original_file et signed_file sont requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Traitement des paramètres
        document_id = request.data.get('document_id')
        if not document_id:
            document_id = str(uuid.uuid4())
        
        original_hash = request.data.get('original_hash')
        signature = request.data.get('signature')
        public_key_pem = request.data.get('public_key_pem')
        title = request.data.get('title')
        
        # Récupérer le propriétaire si un ID est fourni
        owner = None
        owner_id = request.data.get('owner_id')
        if owner_id:
            User = get_user_model()
            try:
                owner = User.objects.get(id=owner_id)
            except User.DoesNotExist:
                logger.warning(f"Propriétaire avec ID {owner_id} non trouvé")
        
        # Récupérer les informations d'organisation et de signataire
        organization_id = request.data.get('organization_id')
        organization_name = request.data.get('organization_name')
        signer_role = request.data.get('signer_role')
        signer_name = request.data.get('signer_name')
        
        # Récupérer l'organisation si un ID est fourni
        organization = None
        if organization_id:
            from users.models import Organization
            try:
                organization = Organization.objects.get(id=organization_id)
                # Si organization_name n'est pas fourni, utiliser le nom de l'organisation trouvée
                if not organization_name:
                    organization_name = organization.name
            except Organization.DoesNotExist:
                logger.warning(f"Organisation avec ID {organization_id} non trouvée")
        
        logger.info(f"Informations de signature - Organisation: {organization_name}, Signataire: {signer_name}, Rôle: {signer_role}")
        
        # Récupérer les fichiers
        original_file = request.FILES['original_file']
        signed_file = request.FILES['signed_file']
        
        # Vérifier si une signature avec cet ID existe déjà
        try:
            existing_signature = DocumentSignature.objects.get(document_id=document_id)
            # Si elle existe, envoyer une erreur
            return Response(
                {"error": f"Une signature avec l'ID {document_id} existe déjà"},
                status=status.HTTP_409_CONFLICT
            )
        except DocumentSignature.DoesNotExist:
            pass
        
        # 🆕 TRAITEMENT DES SIGNATURES ÉPHÉMÈRES (pour store_signature_public)
        signature_type = 'permanent'  # Valeur par défaut
        expiration_date = None
        
        # Extraire les informations de type de signature depuis les métadonnées
        metadata_str = request.data.get('metadata') or request.data.get('user_metadata')
        if metadata_str:
            try:
                import json
                metadata_dict = json.loads(metadata_str)
                logger.info(f"Métadonnées parsées (store_signature_public): {list(metadata_dict.keys())}")
                
                # Extraire le type de signature
                if 'signature_type' in metadata_dict:
                    signature_type = metadata_dict['signature_type']
                    logger.info(f"Type de signature extrait: {signature_type}")
                
                # Extraire la date d'expiration pour les signatures éphémères
                if signature_type == 'ephemeral' and 'expiration_date' in metadata_dict:
                    from django.utils.dateparse import parse_datetime
                    expiration_date = parse_datetime(metadata_dict['expiration_date'])
                    logger.info(f"Date d'expiration extraite: {expiration_date}")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Erreur lors du parsing des métadonnées: {str(e)}")
                # Continuer avec les valeurs par défaut
        
        logger.info(f"Configuration signature (store_signature_public) - Type: {signature_type}, Expiration: {expiration_date}")
        
        # Créer la signature de document
        document_signature = DocumentSignature(
            document_id=document_id,
            original_hash=original_hash,
            signature=signature,
            public_key_pem=public_key_pem,
            title=title,
            owner=owner,
            organization=organization,
            organization_name=organization_name,
            signer_role=signer_role,
            signer_name=signer_name,
            # 🆕 NOUVEAUX CHAMPS POUR SIGNATURES ÉPHÉMÈRES
            signature_type=signature_type,
            expiration_date=expiration_date
        )
        
        # Associer les fichiers
        document_signature.original_file = original_file
        document_signature.signed_file = signed_file
        
        # Enregistrer la signature
        document_signature.save()
        
        # Si l'utilisateur est authentifié, enregistrer l'activité
        if owner:
            ActivityLog.objects.create(
                user=owner,
                action_type='sign',
                description=f"Signature du document: {title or document_id}"
            )
        
        # Journaliser l'opération
        logger.info(f"Signature {document_id} stockée avec succès via l'API publique")
        
        # Renvoyer la réponse
        return Response({
            "status": "success",
            "message": "Signature stockée avec succès",
            "document_id": document_id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Erreur lors du stockage de la signature: {str(e)}")
        return Response(
            {"error": f"Erreur lors du stockage: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
