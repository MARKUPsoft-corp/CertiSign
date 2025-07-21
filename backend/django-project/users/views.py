"""
Vues pour l'API REST des utilisateurs.
"""

import json
import requests
import traceback
from django.core.mail import send_mail
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import IntegrityError
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, Organization, ActivityLog
from .serializers import UserSerializer, OrganizationSerializer, ActivityLogSerializer
from .utils import send_pending_account_notification, get_client_ip
from .views_auth import get_active_organizations, authenticate_with_organization

# Désactiver les avertissements SSL pour le développement
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IsAdminOrSelf(permissions.BasePermission):
    """
    Permission personnalisée pour autoriser seulement les admins et l'utilisateur lui-même.
    """
    def has_object_permission(self, request, view, obj):
        # Autorise les administrateurs
        if request.user.is_superadmin or request.user.is_admin:
            return True
        
        # Autorise l'utilisateur à voir/modifier son propre profil
        return obj == request.user

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les organisations.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'registration_number']
    search_fields = ['name', 'registration_number', 'address']
    ordering_fields = ['name', 'created_at']
    
    def get_permissions(self):
        """
        Seuls les administrateurs peuvent créer, modifier ou supprimer des organisations.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), 
                    permissions.IsAdminUser()]
        return super().get_permissions()

class UserViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les utilisateurs.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'status', 'organization', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'certificate_serial']
    ordering_fields = ['username', 'date_joined', 'last_login']
    
    def get_permissions(self):
        """
        Ajuste les permissions selon l'action.
        - Création (register): accessible à tous (AllowAny)
        - Lecture de la liste : réservée aux administrateurs
        - Actions sur un utilisateur individuel : admin ou l'utilisateur lui-même
        """
        if self.action == 'create' and self.request.path.endswith('/register/'):
            return [permissions.AllowAny()]
        elif self.action == 'list':
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated(), IsAdminOrSelf()]
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approuve un utilisateur en attente.
        Réservé aux super-administrateurs.
        """
        user = self.get_object()
        
        if not request.user.is_superadmin:
            return Response({"detail": "Action réservée aux super-administrateurs"}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        if user.status != 'pending':
            return Response({"detail": "L'utilisateur n'est pas en attente d'approbation"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        user.status = 'active'
        user.save()
        
        # Enregistrer l'activité
        ActivityLog.objects.create(
            user=request.user,
            action_type='status_change',
            description=f"Approbation de l'utilisateur {user.username}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            "detail": "Utilisateur approuvé avec succès",
            "user": UserSerializer(user, context={'request': request}).data
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Rejette un utilisateur en attente.
        Réservé aux super-administrateurs.
        """
        user = self.get_object()
        
        if not request.user.is_superadmin:
            return Response({"detail": "Action réservée aux super-administrateurs"}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        if user.status != 'pending':
            return Response({"detail": "L'utilisateur n'est pas en attente d'approbation"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        user.status = 'rejected'
        user.save()
        
        # Enregistrer l'activité
        ActivityLog.objects.create(
            user=request.user,
            action_type='status_change',
            description=f"Rejet de l'utilisateur {user.username}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            "detail": "Utilisateur rejeté",
            "user": UserSerializer(user, context={'request': request}).data
        })
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        Point d'entrée pour l'inscription des utilisateurs.
        """
        serializer = UserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Renvoie les informations de l'utilisateur connecté.
        """
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

class ActivityLogViewSet(viewsets.ModelViewSet):
    """
    API pour consulter et créer les journaux d'activité.
    La création est utilisée pour enregistrer les activités des utilisateurs.
    """
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'action_type']
    search_fields = ['description', 'ip_address', 'user__username']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']  # Par défaut, du plus récent au plus ancien
    
    def get_permissions(self):
        """
        Ajuste les permissions selon l'action :
        - Création (create) : accessible à tous les utilisateurs authentifiés
        - Liste et détail : réservés aux administrateurs ou à l'utilisateur concerné
        - Modification et suppression : interdites à tous
        """
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]  # En pratique, ces actions ne devraient pas être utilisées
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """
        Les utilisateurs normaux ne peuvent voir que leurs propres activités.
        Les administrateurs peuvent voir toutes les activités.
        """
        if self.request.user.is_admin or self.request.user.is_superadmin:
            return ActivityLog.objects.all()
        return ActivityLog.objects.filter(user=self.request.user)
        
    def perform_create(self, serializer):
        """
        Lors de la création d'une activité, associer automatiquement l'utilisateur connecté
        """
        serializer.save(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def authenticate_user(request):
    """
    Authentifie un utilisateur avec son nom d'utilisateur et mot de passe.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'detail': 'Nom d\'utilisateur et mot de passe requis'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user:
        # Enregistre la connexion
        ActivityLog.objects.create(
            user=user,
            action_type='login',
            description=f"Connexion par identifiants",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'status': user.status,
            'is_active': user.is_active
        })
    
    return Response(
        {'detail': 'Identifiants invalides'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def authenticate_certificate(request):
    """
    Authentifie un utilisateur avec son certificat numérique.
    """
    certificate_serial = request.data.get('certificate_serial')
    certificate_dn = request.data.get('certificate_dn')
    
    if not certificate_serial or not certificate_dn:
        return Response(
            {'detail': 'Numéro de série et DN du certificat requis'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = get_object_or_404(CustomUser, certificate_serial=certificate_serial)
        
        # Vérifie que le DN correspond aussi
        if user.certificate_dn != certificate_dn:
            return Response(
                {'detail': 'Les informations du certificat ne correspondent pas'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Vérifie que l'utilisateur est actif
        if not user.is_active or user.status != 'active':
            return Response(
                {'detail': 'Ce compte n\'est pas actif ou est en attente d\'approbation'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Enregistre la connexion
        ActivityLog.objects.create(
            user=user,
            action_type='login',
            description=f"Connexion par certificat numérique",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'status': user.status,
            'is_active': user.is_active
        })
    
    except CustomUser.DoesNotExist:
        return Response(
            {
                'detail': 'Utilisateur non trouvé',
                'needs_registration': True,
                'certificate_data': {
                    'serial': certificate_serial,
                    'dn': certificate_dn
                }
            }, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def auth_certificate_gateway(request):
    """
    Point d'entrée pour l'authentification et la création d'utilisateur via l'API Gateway.
    Reçoit les informations du certificat extraites par le microservice,
    puis vérifie si l'utilisateur existe ou doit être créé.
    """
    # Vérifier les données reçues
    if not request.data.get('certificate_info'):
        return Response(
            {'detail': 'Informations du certificat manquantes'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cert_info = request.data.get('certificate_info')
    role_requested = request.data.get('role', 'user')
    filename = request.data.get('filename', 'certificate.pfx')
    
    # Extraire les informations clés du certificat
    cert_serial = cert_info.get('serial_number')
    cert_dn = cert_info.get('subject_dn')
    cert_issuer = cert_info.get('issuer_dn')
    cert_email = cert_info.get('email')
    cert_cn = cert_info.get('common_name')
    # Récupérer la date d'expiration et la formater correctement
    cert_expiry_raw = cert_info.get('not_after')
    # Nettoyer la date (supprimer les espaces insécables et autres caractères non désirés)
    if cert_expiry_raw:
        # Supprimer les caractères non désirés et extraire seulement la partie date (YYYY-MM-DD)
        cert_expiry_clean = cert_expiry_raw.strip().replace('\xa0', '')
        # Extraire seulement la partie date (YYYY-MM-DD) du format ISO
        cert_expiry = cert_expiry_clean.split('T')[0] if 'T' in cert_expiry_clean else cert_expiry_clean
    else:
        cert_expiry = None
    
    # Vérifier si les informations essentielles sont présentes
    if not cert_serial or not cert_dn:
        return Response(
            {'detail': 'Informations du certificat incomplètes'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier si le certificat est révoqué
    cert_crl_status = cert_info.get('revocation_status_crl')
    cert_ocsp_status = cert_info.get('revocation_status_ocsp')
    if cert_crl_status == 'révoqué' or cert_ocsp_status == 'révoqué':
        return Response({
            'status': 'revoked',
            'message': 'Votre certificat a été révoqué. Impossible de créer un compte.',
            'certificate_info': {
                'serial': cert_serial,
                'subject_dn': cert_dn,
                'revocation_status_crl': cert_crl_status,
                'revocation_status_ocsp': cert_ocsp_status
            }
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Vérifier si le certificat est expiré
    cert_status = cert_info.get('status')
    if cert_status == 'expiré':
        return Response({
            'status': 'expired',
            'message': 'Votre certificat est expiré. Impossible de créer un compte.',
            'certificate_info': {
                'serial': cert_serial,
                'subject_dn': cert_dn,
                'status': cert_status
            }
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Rechercher un utilisateur existant avec ce certificat
    try:
        user = CustomUser.objects.get(certificate_serial=cert_serial)
        
        # Vérifier si l'utilisateur tente de s'authentifier avec un rôle différent
        if role_requested == 'admin' and user.role == 'user':
            # Un utilisateur standard essaie de se connecter en tant qu'administrateur
            return Response({
                'status': 'error',
                'message': 'Un utilisateur est déjà enregistré avec ce certificat. Impossible de se connecter en tant qu\'administrateur.'
            })
        elif role_requested == 'user' and (user.role == 'admin' or user.role == 'superadmin'):
            # Un administrateur ou superadmin existe déjà avec ce certificat et quelqu'un essaie de se connecter en tant qu'utilisateur
            return Response({
                'status': 'error',
                'message': 'Ce certificat appartient à un administrateur. Vous n\'êtes pas autorisé à vous connecter en tant qu\'utilisateur.'
            })
            
        # Vérifier le statut du compte
        if user.status == 'pending':
            # Compte en attente de validation
            return Response({
                'status': 'pending',
                'message': 'Votre compte est en attente de validation par un administrateur.'
            })
        elif user.status == 'rejected':
            # Compte rejeté
            return Response({
                'status': 'rejected',
                'message': 'Votre demande de création de compte a été rejetée.'
            })
        elif user.status == 'active':
            # Compte actif - Authentification réussie
            # Enregistrer l'activité de connexion
            ActivityLog.objects.create(
                user=user,
                action_type='login',
                description=f"Connexion par certificat PFX via API Gateway en tant que {user.role}",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            # Message de bienvenue personnalisé selon le rôle
            welcome_message = 'Authentification réussie'
            if user.role == 'admin':
                welcome_message = 'Bienvenue dans votre espace administrateur d\'organisation'
            elif user.role == 'superadmin':
                welcome_message = 'Bienvenue dans votre espace super administrateur'
            
            # Renvoyer les informations de l'utilisateur
            return Response({
                'status': 'active',
                'message': welcome_message,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'certificate_info': {
                    'serial': cert_serial,
                    'subject_dn': cert_dn,
                    'issuer_dn': cert_issuer,
                    'common_name': cert_cn,
                    'expiry_date': cert_expiry,
                    'filename': filename
                }
            })
    
    except CustomUser.DoesNotExist:
        # L'utilisateur n'existe pas encore - Créer un nouveau compte en attente
        # Générer un nom d'utilisateur unique basé sur le CN ou l'email
        base_username = cert_email.split('@')[0] if cert_email else cert_cn.replace(' ', '_').lower()
        username = base_username
        
        # S'assurer que le nom d'utilisateur est unique
        counter = 1
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        # Créer le nouvel utilisateur
        try:
            user = CustomUser.objects.create(
                username=username,
                email=cert_email or f"{username}@example.com",  # Utiliser l'email du certificat ou un email par défaut
                first_name=cert_cn.split(' ')[0] if cert_cn and ' ' in cert_cn else cert_cn or '',
                last_name=cert_cn.split(' ')[1] if cert_cn and ' ' in cert_cn else '',
                certificate_serial=cert_serial,
                certificate_dn=cert_dn,
                certificate_expiry=cert_expiry,
                role=role_requested,  # Rôle demandé, mais sous réserve d'approbation
                status='pending',  # Statut en attente d'approbation
                is_active=True  # Compte actif mais en attente
            )
            
            # Définir un mot de passe aléatoire (l'utilisateur s'authentifiera via certificat)
            import secrets
            import string
            # Générer un mot de passe aléatoire de 12 caractères
            alphabet = string.ascii_letters + string.digits + string.punctuation
            random_password = ''.join(secrets.choice(alphabet) for _ in range(12))
            user.set_password(random_password)
            user.save()
            
            # Enregistrer l'activité de création de compte
            ActivityLog.objects.create(
                user=user,
                action_type='status_change',
                description=f"Création de compte via certificat PFX - En attente d'approbation",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            # Informer que le compte a été créé et est en attente de validation
            return Response({
                'status': 'pending',
                'message': 'Votre compte a été créé et est en attente de validation par un administrateur.',
                'username': user.username,
                'certificate_info': {
                    'serial': cert_serial,
                    'subject_dn': cert_dn
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # En cas d'erreur lors de la création du compte
            return Response({
                'status': 'error',
                'message': f'Erreur lors de la création du compte: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_admin_certificate(request):
    """
    Vérifie si un certificat est valide pour l'authentification d'un administrateur d'organisation.
    Renvoie également les informations de l'organisation si elle existe déjà.
    """
    # Vérifier les données reçues
    if not request.data:
        return Response(
            {'detail': 'Données manquantes'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    certificate = request.data.get('certificate')
    password = request.data.get('password')
    role_requested = request.data.get('role', 'admin')
    
    if not certificate or not password:
        return Response(
            {'detail': 'Certificat et mot de passe requis'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier si le rôle demandé est bien admin
    if role_requested != 'admin':
        return Response({
            'valid': False,
            'errorTitle': 'Rôle invalide',
            'errorMessage': 'Cette vérification est uniquement pour les administrateurs d\'organisation'
        })
    
    # Envoyer d'abord le certificat au microservice pour extraire les informations
    try:
        # Utiliser l'API Gateway pour extraire les informations du certificat - Via Nginx
        gateway_url = "https://ppd.camgovca.cm/cert/extract-cert-info-base64/"
        gateway_response = requests.post(
            gateway_url,
            json={
                'certificate_base64': certificate,
                'password': password
            },
            verify=False  # Désactiver la vérification SSL pour le développement
        )
        
        if gateway_response.status_code != 200:
            return Response({
                'valid': False,
                'errorTitle': 'Erreur d\'extraction',
                'errorMessage': 'Erreur lors de l\'extraction des informations du certificat. Vérifiez votre mot de passe.'
            })
            
        cert_info = gateway_response.json()
        
        # Extraire les informations clés du certificat
        cert_serial = cert_info.get('serial_number')
        cert_dn = cert_info.get('subject_dn')
        
        # Vérifier si le certificat est révoqué ou expiré
        cert_crl_status = cert_info.get('revocation_status_crl')
        cert_ocsp_status = cert_info.get('revocation_status_ocsp')
        cert_status = cert_info.get('status')
        
        if cert_crl_status == 'révoqué' or cert_ocsp_status == 'révoqué':
            return Response({
                'valid': False,
                'errorTitle': 'Certificat révoqué',
                'errorMessage': 'Votre certificat a été révoqué. Impossible de continuer.'
            })
        
        if cert_status == 'expiré':
            return Response({
                'valid': False,
                'errorTitle': 'Certificat expiré',
                'errorMessage': 'Votre certificat est expiré. Impossible de continuer.'
            })
        
        try:
            # Vérifier si un utilisateur existe déjà avec ce certificat
            user = CustomUser.objects.get(certificate_serial=cert_serial)
            
            # Vérifier si le rôle correspond
            if user.role != 'admin':
                return Response({
                    'valid': False,
                    'errorTitle': 'Accès refusé',
                    'errorMessage': "Ce certificat appartient à un utilisateur de type " + user.get_role_display() + ". Impossible d'accéder à l'administration d'organisation."
                })
            
            # Si l'utilisateur est un administrateur, vérifier son statut
            if user.status != 'active':
                if user.status == 'pending':
                    return Response({
                        'valid': False,
                        'errorTitle': 'Compte en attente',
                        'errorMessage': "Votre compte administrateur est en attente de validation. Veuillez contacter un super administrateur."
                    })
                else:  # rejected
                    return Response({
                        'valid': False,
                        'errorTitle': 'Compte refusé',
                        'errorMessage': "Votre compte administrateur a été refusé. Veuillez contacter un super administrateur."
                    })
            
            # Si l'utilisateur est un administrateur actif, vérifier son organisation
            if user.organization:
                # Vérifier le statut de l'organisation
                if user.organization.status != 'active':
                    if user.organization.status == 'pending':
                        return Response({
                            'valid': False,
                            'errorTitle': 'Organisation en attente',
                            'errorMessage': "Votre organisation est en attente de validation. Veuillez contacter un super administrateur."
                        })
                    else:  # rejected
                        return Response({
                            'valid': False,
                            'errorTitle': 'Organisation refusée',
                            'errorMessage': "Votre organisation a été refusée. Veuillez contacter un super administrateur."
                        })
                
                # Si l'administrateur et l'organisation sont actifs, connexion directe
                return Response({
                    'valid': True,
                    'exists': True,   # Indique que c'est un administrateur existant (pas besoin de modale)
                    'organization': {
                        'id': user.organization.id,
                        'name': user.organization.name,
                        'registration_number': user.organization.registration_number,
                        'address': user.organization.address or ''
                    },
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                })
            else:
                # Admin sans organisation (rare, mais possible)
                return Response({
                    'valid': True,
                    'exists': True,   # Indique que c'est un administrateur existant
                    'message': "Veuillez compléter les informations de votre organisation."
                })
        
        except CustomUser.DoesNotExist:
            # Aucun utilisateur avec ce certificat, on peut créer un nouveau compte admin
            return Response({
                'valid': True,
                'message': "Veuillez compléter les informations de votre organisation pour créer votre compte administrateur."
            })
            
    except Exception as e:
        return Response({
            'valid': False,
            'errorTitle': 'Erreur système',
            'errorMessage': f"Une erreur s'est produite lors de la vérification: {str(e)}"
        })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def authenticate_org_admin(request):
    """
    Authentifie ou crée un administrateur d'organisation avec les informations d'organisation fournies.
    """
    # Vérifier les données reçues
    if not request.data.get('organization'):
        return Response(
            {'detail': 'Informations de l\'organisation manquantes'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Récupérer les données
    certificate_data = request.data
    org_data = request.data.get('organization')
    
    # Vérifier si les informations de l'organisation sont complètes
    if not org_data.get('name') or not org_data.get('registration_number'):
        return Response(
            {'detail': 'Nom et numéro d\'immatriculation de l\'organisation requis'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Envoyer d'abord le certificat au microservice pour extraire les informations
    try:
        # Utiliser l'API Gateway pour extraire les informations du certificat - Via Nginx
        gateway_url = "https://ppd.camgovca.cm/cert/extract-cert-info-base64/"
        gateway_response = requests.post(
            gateway_url,
            json={
                'certificate_base64': certificate_data.get('certificate'),
                'password': certificate_data.get('password')
            },
            verify=False  # Désactiver la vérification SSL pour le développement
        )
        
        if gateway_response.status_code != 200:
            return Response(
                {'detail': 'Erreur lors de l\'extraction des informations du certificat'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        cert_info = gateway_response.json()
        
        # Extraire les informations clés du certificat
        cert_serial = cert_info.get('serial_number')
        cert_dn = cert_info.get('subject_dn')
        cert_cn = cert_info.get('common_name')
        cert_email = cert_info.get('email')
        cert_expiry = cert_info.get('not_after').split('T')[0] if 'T' in cert_info.get('not_after', '') else cert_info.get('not_after')
        
        # Vérifier si une organisation existe déjà avec ce numéro d'immatriculation
        try:
            organization = Organization.objects.get(registration_number=org_data.get('registration_number'))
            
            # Vérifier le statut de l'organisation
            if organization.status == 'rejected':
                return Response({
                    'status': 'error',
                    'message': "Cette organisation a été refusée par un administrateur. Veuillez contacter le support."
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Mettre à jour les informations si nécessaire
            if organization.name != org_data.get('name'):
                organization.name = org_data.get('name')
            if org_data.get('address') and organization.address != org_data.get('address'):
                organization.address = org_data.get('address')
            if org_data.get('email') and organization.email != org_data.get('email'):
                organization.email = org_data.get('email')
            organization.save()
        except Organization.DoesNotExist:
            # Créer une nouvelle organisation (en statut pending par défaut)
            organization = Organization.objects.create(
                name=org_data.get('name'),
                registration_number=org_data.get('registration_number'),
                address=org_data.get('address', ''),
                email=org_data.get('email', ''),  # Ajout du champ email
                status='pending'  # Les nouvelles organisations sont en attente de validation
            )
        
        # Vérifier si un utilisateur existe déjà avec ce certificat
        try:
            user = CustomUser.objects.get(certificate_serial=cert_serial)
            
            # Vérifier le rôle
            if user.role != 'admin':
                return Response({
                    'status': 'error',
                    'message': "Ce certificat appartient à un utilisateur de type " + user.get_role_display() + ". Impossible d'accéder à l'administration d'organisation."
                })
            
            # Vérifier le statut de l'utilisateur
            if user.status != 'active':
                return Response({
                    'status': user.status,
                    'message': "Votre compte administrateur est " + ("en attente de validation" if user.status == 'pending' else "refusé") + ". Veuillez contacter un super administrateur."
                })
            
            # Mettre à jour l'organisation si nécessaire
            if user.organization != organization:
                user.organization = organization
                user.save()
            
            # Enregistrer l'activité de connexion
            ActivityLog.objects.create(
                user=user,
                action_type='login',
                description=f"Connexion en tant qu'administrateur d'organisation via certificat PFX",
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            # Adapter le message selon le statut de l'organisation
            status_message = f"Bienvenue, {user.first_name}. Vous êtes connecté en tant qu'administrateur de {organization.name}."
            if organization.status == 'pending':
                status_message += " Votre organisation est en attente de validation par un super administrateur."
            
            # Renvoyer les informations de l'utilisateur et de l'organisation
            return Response({
                'status': 'active',
                'org_status': organization.status,  # Inclure le statut de l'organisation
                'message': status_message,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': 'admin',
                'organization': {
                    'id': organization.id,
                    'name': organization.name,
                    'registration_number': organization.registration_number,
                    'address': organization.address,
                    'status': organization.status
                },
                'certificate_info': {
                    'serial': cert_serial,
                    'subject_dn': cert_dn,
                    'common_name': cert_cn,
                    'expiry_date': cert_expiry,
                    'filename': certificate_data.get('filename', 'certificate.pfx')
                }
            })
            
        except CustomUser.DoesNotExist:
            # Créer un nouvel administrateur
            # Générer un nom d'utilisateur unique basé sur le CN ou l'email
            base_username = cert_email.split('@')[0] if cert_email else cert_cn.replace(' ', '_').lower() if cert_cn else 'admin'
            username = base_username
            
            # S'assurer que le nom d'utilisateur est unique
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            # Déterminer le statut de l'administrateur en fonction de la configuration du système
            # Les administrateurs d'organisation peuvent être soit activés directement, soit mis en attente selon la politique
            admin_status = 'pending'  # Par défaut, les administrateurs sont en attente de validation
            
            # Vérifier s'il existe un paramètre permettant l'activation directe des administrateurs
            # (Vous pourriez ajouter cette configuration dans les paramètres du site)
            # Si un super admin a déjà été créé, les nouveaux comptes admin doivent être validés
            if CustomUser.objects.filter(role='superadmin').exists():
                admin_status = 'pending'
            else:
                # Si aucun super admin n'existe encore, activer directement
                admin_status = 'active'
            
            # Créer le nouvel administrateur
            user = CustomUser.objects.create(
                username=username,
                email=cert_email or f"{username}@example.com",
                first_name=cert_cn.split(' ')[0] if cert_cn and ' ' in cert_cn else cert_cn or '',
                last_name=cert_cn.split(' ')[1] if cert_cn and ' ' in cert_cn else '',
                certificate_serial=cert_serial,
                certificate_dn=cert_dn,
                certificate_expiry=cert_expiry,
                role='admin',
                organization=organization,
                status=admin_status,
                is_active=True  # Le compte est actif dans Django même s'il est en attente d'approbation
            )
            
            # Définir un mot de passe aléatoire
            alphabet = string.ascii_letters + string.digits + string.punctuation
            random_password = ''.join(secrets.choice(alphabet) for _ in range(12))
            user.set_password(random_password)
            user.save()
            
            # Description de l'activité basée sur le statut
            activity_desc = ("Création de compte administrateur d'organisation " + 
                           ("(en attente)" if user.status == 'pending' else "(actif)") + 
                           " via certificat PFX")
            
            # Enregistrer l'activité de création de compte
            ActivityLog.objects.create(
                user=user,
                action_type='status_change',
                description=activity_desc,
                ip_address=get_client_ip(request)
            )
            
            # Envoyer un email de notification au super admin si l'organisation ou l'admin est en attente
            if organization.status == 'pending' or user.status == 'pending':
                send_pending_account_notification(user, organization, is_admin=True)
            
            # Adapter le message selon le statut
            status_message = f"Votre compte administrateur pour {organization.name} a été créé avec succès."
            
            # Ajouter des informations sur le statut si nécessaire
            if user.status == 'pending':
                status_message += " Il est en attente de validation par un super administrateur."
            
            if organization.status == 'pending':
                status_message += " Votre organisation est également en attente de validation."
            
            # Renvoyer les informations de l'utilisateur et de l'organisation
            return Response({
                'status': user.status,
                'org_status': organization.status,
                'message': status_message,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': 'admin',
                'organization': {
                    'id': organization.id,
                    'name': organization.name,
                    'registration_number': organization.registration_number,
                    'address': organization.address,
                    'status': organization.status
                },
                'certificate_info': {
                    'serial': cert_serial,
                    'subject_dn': cert_dn,
                    'common_name': cert_cn,
                    'expiry_date': cert_expiry,
                    'filename': certificate_data.get('filename', 'certificate.pfx')
                }
            })
    
    except Exception as e:
        return Response(
            {'detail': f'Erreur lors de l\'authentification: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@receiver(post_save, sender=CustomUser)
def send_pending_approval_email(sender, instance, created, **kwargs):
    """
    Envoyer un email de notification à l'administrateur lorsqu'un nouveau compte est en attente d'approbation.
    """
    # Ne s'exécute que si c'est une nouvelle instance et que son statut est "pending"
    if created and instance.status == 'pending':
        # Ajouter la logique d'envoi d'email ici (à implémenter)
        pass

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_homepage_stats(request):
    """
    Récupère les statistiques globales pour la homepage.
    Accessible sans authentification pour afficher sur la page d'accueil.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from documents.models import DocumentSignature
        
        # Compter les utilisateurs actifs
        active_users_count = CustomUser.objects.filter(status='active').count()
        
        # Compter les documents signés
        signed_documents_count = DocumentSignature.objects.count()
        
        # Autres statistiques (fixes pour l'instant)
        availability = "99.9%"
        legal_compliance = "100%"
        
        stats = {
            'signed_documents': signed_documents_count,
            'active_users': active_users_count,
            'availability': availability,
            'legal_compliance': legal_compliance
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        return Response(
            {'detail': 'Erreur lors de la récupération des statistiques'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )