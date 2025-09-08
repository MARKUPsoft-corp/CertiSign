"""
Vues d'authentification pour le module users de CertiSign.
Ce fichier contient les vues d'API liées à l'authentification des utilisateurs.
"""
import logging
import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Organization
from .utils import send_pending_account_notification, get_client_ip
from .serializers import OrganizationSerializer
import ssl
import requests.packages.urllib3.util.ssl_

logger = logging.getLogger(__name__)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@ensure_csrf_cookie
def get_active_organizations(request):
    """
    Récupère la liste des organisations actives.
    Utilisé par l'interface de connexion pour permettre aux utilisateurs
    de sélectionner leur organisation.
    """
    try:
        # Récupérer uniquement les organisations actives
        organizations = Organization.objects.filter(status='active')
        
        # Sérialiser les données
        serializer = OrganizationSerializer(organizations, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des organisations actives: {e}")
        return Response(
            {'detail': 'Erreur lors de la récupération des organisations'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def authenticate_with_organization(request):
    """
    Authentifie un utilisateur avec son certificat et l'associe à une organisation.
    Si l'utilisateur n'existe pas, crée un nouvel utilisateur en attente.
    Si l'organisation_id est "none", l'utilisateur n'est associé à aucune organisation.
    """
    # Vérifier les données reçues
    if not request.data:
        return Response(
            {'detail': 'Données manquantes'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Récupérer les données
    certificate = request.data.get('certificate')
    password = request.data.get('password')
    organization_id = request.data.get('organization_id')
    
    if not certificate or not password:
        return Response(
            {'detail': 'Certificat et mot de passe requis'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Extraire les informations du certificat via le microservice
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
                'status': 'error',
                'message': 'Erreur lors de l\'extraction des informations du certificat. Vérifiez votre mot de passe.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        cert_info = gateway_response.json()
        
        # Extraire les informations clés du certificat
        cert_serial = cert_info.get('serial_number')
        cert_dn = cert_info.get('subject_dn')
        cert_cn = cert_info.get('common_name')
        cert_email = cert_info.get('email')
        cert_expiry = cert_info.get('not_after').split('T')[0] if 'T' in cert_info.get('not_after', '') else cert_info.get('not_after')
        
        # Vérifier si le certificat est révoqué ou expiré
        cert_crl_status = cert_info.get('revocation_status_crl')
        cert_ocsp_status = cert_info.get('revocation_status_ocsp')
        cert_status = cert_info.get('status')
        
        if cert_crl_status == 'révoqué' or cert_ocsp_status == 'révoqué':
            return Response({
                'status': 'error',
                'message': 'Votre certificat a été révoqué. Impossible de continuer.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if cert_status == 'expiré':
            return Response({
                'status': 'error',
                'message': 'Votre certificat est expiré. Impossible de continuer.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Récupérer l'organisation si un ID est fourni et différent de "none"
        organization = None
        if organization_id and organization_id != "none":
            try:
                organization = Organization.objects.get(id=organization_id)
                if organization.status != 'active':
                    return Response({
                        'status': 'error',
                        'message': f"L'organisation sélectionnée n'est pas active ({organization.get_status_display()})"
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Organization.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': "L'organisation sélectionnée n'existe pas"
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si un utilisateur existe déjà avec ce certificat
        try:
            user = CustomUser.objects.get(certificate_serial=cert_serial)
            
            # Vérifier le statut de l'utilisateur
            if user.status != 'active':
                return Response({
                    'status': user.status,
                    'message': "Votre compte est " + ("en attente de validation" if user.status == 'pending' else "refusé") + ". Veuillez contacter un administrateur."
                })
                
            # Vérifier la correspondance entre l'organisation sélectionnée et celle associée au certificat
            # Pour les administrateurs, collaborateurs et signataires uniquement
            if organization_id == "none" and user.organization and user.role in ['admin', 'superadmin', 'collaborator', 'signer']:
                # L'utilisateur avec rôle administratif a sélectionné "Aucune organisation" mais son certificat est associé à une organisation
                logger.info(f"Utilisateur {user.username} avec rôle {user.role} a sélectionné 'aucune organisation' mais est associé à {user.organization.name}")
                return Response({
                    'status': 'mismatch',
                    'message': f"Votre certificat est associé à l'organisation {user.organization.name}. Veuillez la sélectionner pour vous connecter.",
                    'suggested_organization': {
                        'id': user.organization.id,
                        'name': user.organization.name
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Si l'utilisateur est un compte simple, on lui permet de s'authentifier sans organisation
            if organization_id == "none" and user.organization and user.role == 'user':
                logger.info(f"Utilisateur simple {user.username} s'authentifie sans organisation bien qu'il soit associé à {user.organization.name}")
                # Nous permettons à l'utilisateur simple de continuer, sans bloquer
                
            # Ajouter des logs pour débogage
            logger.info(f"Organization_id (type {type(organization_id)}): {organization_id}")
            if user.organization:
                logger.info(f"User organization id (type {type(user.organization.id)}): {user.organization.id}")
                logger.info(f"User role: {user.role}")
            
            # Vérification améliorée pour comparer les IDs correctement - uniquement pour les rôles administratifs
            if organization_id != "none" and user.organization and user.role in ['admin', 'superadmin', 'collaborator', 'signer']:
                # Convertir les deux valeurs en chaînes pour une comparaison cohérente
                user_org_id_str = str(user.organization.id)
                selected_org_id_str = str(organization_id)
                
                logger.info(f"Comparing user_org_id_str: {user_org_id_str} with selected_org_id_str: {selected_org_id_str}")
                
                if user_org_id_str != selected_org_id_str:
                    # L'utilisateur avec rôle administratif a sélectionné une organisation différente de celle associée à son certificat
                    return Response({
                        'status': 'mismatch',
                        'message': f"Votre certificat est associé à l'organisation {user.organization.name}, mais vous avez sélectionné une autre organisation.",
                        'suggested_organization': {
                            'id': user.organization.id,
                            'name': user.organization.name
                        }
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Pour les utilisateurs simples, on ne vérifie pas cette correspondance
            # Ils peuvent sélectionner n'importe quelle organisation, mais on les informera qu'ils n'ont pas accès à l'organisation
            
            # Vérification si l'utilisateur est un compte simple (non administrateur) essayant de sélectionner une organisation
            # Cette vérification ne s'applique que si l'utilisateur sélectionne une organisation spécifique
            if organization_id != "none" and user.role not in ['admin', 'superadmin', 'collaborator', 'signer']:
                # L'utilisateur a un rôle simple mais essaie de sélectionner une organisation
                try:
                    org = Organization.objects.get(id=organization_id)
                    # Message d'erreur personnalisé et plus convivial pour les utilisateurs simples
                    return Response({
                        'status': 'error',
                        'message': f"En tant qu'utilisateur simple, vous ne pouvez pas vous connecter à l'organisation {org.name}. Si vous avez besoin d'accéder à cette organisation, veuillez contacter l'administrateur pour qu'il vous attribue un rôle de collaborateur ou signataire.",
                        'error_code': 'simple_user_org_access_denied',
                        'organization_name': org.name
                    }, status=status.HTTP_403_FORBIDDEN)
                except Organization.DoesNotExist:
                    return Response({
                        'status': 'error',
                        'message': "L'organisation sélectionnée n'existe pas."
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérification que l'utilisateur n'a pas d'organisation mais en a sélectionné une
            if organization_id != "none" and not user.organization:
                # Si l'utilisateur n'a pas encore d'organisation associée, on peut mettre à jour son profil
                try:
                    org = Organization.objects.get(id=organization_id)
                    # Vérifier si l'utilisateur a un rôle qui lui permet d'être associé à une organisation
                    if user.role in ['admin', 'collaborator', 'signer']:
                        user.organization = org
                        user.save()
                        logger.info(f"Utilisateur {user.username} associé à l'organisation {org.name}")
                    else:
                        # Message d'erreur convivial et explicatif pour les utilisateurs simples
                        return Response({
                            'status': 'error',
                            'message': f"En tant qu'utilisateur simple, vous ne pouvez pas vous connecter à l'organisation {org.name}. Veuillez sélectionner 'Aucune organisation' ou contactez un administrateur pour obtenir un rôle de collaborateur ou signataire.",
                            'error_code': 'simple_user_org_access_denied',
                            'organization_name': org.name,
                            'suggested_action': 'select_none'
                        }, status.HTTP_403_FORBIDDEN)
                except Organization.DoesNotExist:
                    # Ne devrait pas arriver car on a déjà vérifié l'existence plus tôt
                    pass
            
            # Pour un utilisateur existant, on retourne son rôle et son organisation actuels
            # sans modifier ses informations
            serialized_org = None
            if user.organization:
                serialized_org = {
                    'id': user.organization.id,
                    'name': user.organization.name,
                    'registration_number': user.organization.registration_number,
                    'status': user.organization.status
                }
            
            # Générer un token JWT pour l'utilisateur authentifié
            refresh = RefreshToken.for_user(user)
            
            # Logger l'authentification réussie
            logger.info(f"Authentification réussie pour {user.username} avec token JWT généré")
            
            # Retourner la réponse avec le token JWT
            return Response({
                'status': 'active',
                'message': f"Bienvenue, {user.full_name}. Vous êtes connecté en tant que {user.get_role_display()}.",
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'organization': serialized_org,
                'certificate_info': {
                    'serial': cert_serial,
                    'subject_dn': cert_dn,
                    'common_name': cert_cn,
                    'expiry_date': cert_expiry,
                    'filename': request.data.get('filename', '')
                },
                # Ajouter le token d'accès et le token de rafraîchissement
                'token': str(refresh.access_token),
                'refresh': str(refresh)
            })
            
        except CustomUser.DoesNotExist:
            # Créer un nouvel utilisateur
            # Générer un nom d'utilisateur unique basé sur le nom commun du certificat
            username = cert_cn.lower().replace(' ', '.') if cert_cn else f"user_{cert_serial[-8:]}"
            count = 0
            base_username = username
            while CustomUser.objects.filter(username=username).exists():
                count += 1
                username = f"{base_username}_{count}"
            
            # Extraire prénom et nom du CN
            name_parts = cert_cn.split() if cert_cn else ['Utilisateur', 'Inconnu']
            first_name = name_parts[0] if len(name_parts) > 0 else 'Utilisateur'
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else 'Inconnu'
            
            # Créer l'utilisateur avec statut 'pending'
            user = CustomUser.objects.create(
                username=username,
                email=cert_email or f"{username}@example.com",
                first_name=first_name,
                last_name=last_name,
                certificate_serial=cert_serial,
                certificate_dn=cert_dn,
                certificate_expiry=cert_expiry,
                organization=organization,
                status='pending',  # Par défaut en attente de validation
                role='user'  # Rôle par défaut: utilisateur simple
            )
            
            # Envoyer une notification au super admin
            send_pending_account_notification(user, organization, is_admin=False)
            
            # Retourner la réponse avec les informations de l'utilisateur créé
            serialized_org = None
            if organization:
                serialized_org = {
                    'id': organization.id,
                    'name': organization.name,
                    'registration_number': organization.registration_number,
                    'status': organization.status
                }
            
            # Pour un compte en attente, nous pouvons aussi générer un token JWT limité
            # qui permettra à l'utilisateur de consulter le statut de sa demande
            refresh = RefreshToken.for_user(user)
            
            logger.info(f"Compte en attente créé pour {user.username} avec token JWT généré")
            
            return Response({
                'status': 'pending',
                'message': "Votre compte a été créé et est en attente de validation par un administrateur. Vous recevrez une notification par email une fois votre compte validé.",
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'organization': serialized_org,
                'certificate_info': {
                    'serial': cert_serial,
                    'subject_dn': cert_dn,
                    'common_name': cert_cn,
                    'expiry_date': cert_expiry,
                    'filename': request.data.get('filename', '')
                },
                # Ajouter le token d'accès et le token de rafraîchissement
                'token': str(refresh.access_token),
                'refresh': str(refresh)
            })
    
    except Exception as e:
        logger.error(f"Erreur lors de l'authentification avec organisation: {e}")
        return Response({
            'status': 'error',
            'message': f"Une erreur est survenue lors de l'authentification: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
