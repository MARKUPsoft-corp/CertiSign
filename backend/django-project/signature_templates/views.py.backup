from django.shortcuts import render
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings
import os
from .models import SignatureTemplate
from .serializers import (
    SignatureTemplateSerializer,
    SignatureTemplateListSerializer,
    SignatureTemplateCreateSerializer
)
from documents.utils import get_sftp_file_response, get_sftp_preview_response  # Ajout de l'import SFTP

class IsOwnerOrOrganizationMember(permissions.BasePermission):
    """
    Permission personnalisée pour permettre aux propriétaires et membres d'organisation de gérer les templates.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Les permissions de lecture sont autorisées pour toute requête
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Le propriétaire du template peut tout faire
        if obj.user == user:
            return True
        
        # Les collaborateurs et signataires peuvent gérer les templates de leur organisation
        if user.organization and obj.organization_name == user.organization.name:
            # Vérifier le rôle de l'utilisateur
            if user.is_collaborator or user.is_signer or user.is_org_admin:
                return True
        
        # Les super admins Django peuvent tout faire
        if user.is_superuser:
            return True
        
        # Les super admins personnalisés peuvent tout faire
        if hasattr(user, 'is_superadmin') and user.is_superadmin:
            return True
        
        return False

class SignatureTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint pour les templates de signature.
    """
    queryset = SignatureTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrOrganizationMember]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SignatureTemplateCreateSerializer
        elif self.action in ['list', 'retrieve']:
            return SignatureTemplateListSerializer
        return SignatureTemplateSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Les super admins peuvent voir tous les templates
        if user.is_superuser:
            return SignatureTemplate.objects.all().order_by('-created_at')
        
        # Filtrer par organisation si spécifié
        organization_name = self.request.query_params.get('organization_name', None)

        if organization_name:
            # Si un nom d'organisation est spécifié, retourner seulement les templates de cette organisation
            # Vérifier que l'utilisateur a accès à cette organisation
            if user.organization and user.organization.name == organization_name:
                # Utilisateur appartient à l'organisation demandée
                return SignatureTemplate.objects.filter(organization_name=organization_name).order_by('-created_at')
            elif not user.organization:
                # Utilisateur sans organisation ne peut pas accéder aux templates d'organisation
                return SignatureTemplate.objects.none()
            else:
                # Utilisateur demande une organisation différente de la sienne
                return SignatureTemplate.objects.none()
        
        # Comportement par défaut selon l'organisation de l'utilisateur
        if user.organization:
            # Utilisateur appartient à une organisation : retourner tous les templates de cette organisation
            return SignatureTemplate.objects.filter(
                organization_name=user.organization.name
            ).order_by('-created_at')
        else:
            # Utilisateur sans organisation : retourner seulement ses propres templates
            return SignatureTemplate.objects.filter(user=user).order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def preview_document(self, request, pk=None):
        """
        Afficher l'aperçu du document dans l'iframe (pas de téléchargement)
        """
        template = self.get_object()
        if not template.preview_document:
            return Response(
                {"detail": "Aucun aperçu disponible pour ce template."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Utiliser l'utilitaire SFTP pour l'affichage (pas le téléchargement)
        import os
        return get_sftp_preview_response(
            template.preview_document,
            content_type='application/pdf'
        )
    
    @action(detail=True, methods=['get'])
    def download_preview(self, request, pk=None):
        """
        Télécharger l'aperçu du document généré
        """
        template = self.get_object()
        if not template.preview_document:
            return Response(
                {"detail": "Aucun aperçu disponible pour ce template."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Utiliser l'utilitaire SFTP pour le téléchargement
        import os
        return get_sftp_file_response(
            template.preview_document,
            filename=os.path.basename(template.preview_document.name) if template.preview_document.name else None
        )
    
    @action(detail=True, methods=['get'])
    def download_original(self, request, pk=None):
        """
        Télécharger le document original
        """
        template = self.get_object()
        if not template.original_document:
            return Response(
                {"detail": "Aucun document original disponible pour ce template."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Utiliser l'utilitaire SFTP pour le téléchargement
        import os
        return get_sftp_file_response(
            template.original_document,
            filename=os.path.basename(template.original_document.name) if template.original_document.name else None
        )
    
    @action(detail=True, methods=['get'])
    def download_signature_image(self, request, pk=None):
        """
        Télécharger l'image de signature
        """
        template = self.get_object()
        if not template.signature_image:
            return Response(
                {"detail": "Aucune image de signature disponible pour ce template."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Utiliser l'utilitaire SFTP pour le téléchargement
        import os
        return get_sftp_file_response(
            template.signature_image,
            filename=os.path.basename(template.signature_image.name) if template.signature_image.name else None
        )

# Vues simples pour les opérations de liste et de détail
class SignatureTemplateList(generics.ListCreateAPIView):
    """
    Liste tous les templates de signature de l'utilisateur ou en crée un nouveau.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SignatureTemplateCreateSerializer
        return SignatureTemplateListSerializer
    
    def get_queryset(self):
        user = self.request.user
        return SignatureTemplate.objects.filter(user=user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SignatureTemplateDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Récupère, met à jour ou supprime un template de signature.
    """
    serializer_class = SignatureTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrOrganizationMember]
    
    def get_queryset(self):
        user = self.request.user
        return SignatureTemplate.objects.filter(user=user)
