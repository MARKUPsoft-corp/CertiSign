from django.shortcuts import render
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponse
from django.conf import settings
import os

from .models import SignatureTemplate
from .serializers import (
    SignatureTemplateSerializer,
    SignatureTemplateListSerializer,
    SignatureTemplateCreateSerializer
)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour permettre uniquement aux propriétaires d'un objet de le modifier.
    """
    def has_object_permission(self, request, view, obj):
        # Les permissions de lecture sont autorisées pour toute requête
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Les permissions d'écriture sont uniquement autorisées pour le propriétaire
        return obj.user == request.user

class SignatureTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint pour les templates de signature.
    """
    queryset = SignatureTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SignatureTemplateListSerializer
        elif self.action == 'create':
            return SignatureTemplateCreateSerializer
        return SignatureTemplateSerializer
    
    def get_queryset(self):
        """
        Filtrer les templates pour ne montrer que ceux de l'utilisateur connecté
        ou ceux de son organisation s'il en a une.
        """
        user = self.request.user
        queryset = SignatureTemplate.objects.filter(user=user)
        
        # Si l'utilisateur a une organisation, ajouter les templates de l'organisation
        if hasattr(user, 'profile') and user.profile.organization:
            org_templates = SignatureTemplate.objects.filter(
                organization_name=user.profile.organization.name
            ).exclude(user=user)  # Exclure ceux déjà inclus
            queryset = queryset | org_templates
        
        return queryset.order_by('-created_at')
    
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
        
        # Construire le chemin du fichier
        file_path = os.path.join(settings.MEDIA_ROOT, template.preview_document.name)
        
        if not os.path.exists(file_path):
            return Response(
                {"detail": "Le fichier d'aperçu n'existe pas."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Ouvrir et retourner le fichier
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{template.get_file_name()}"'
            return response
    
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
        
        # Construire le chemin du fichier
        file_path = os.path.join(settings.MEDIA_ROOT, template.original_document.name)
        
        if not os.path.exists(file_path):
            return Response(
                {"detail": "Le fichier original n'existe pas."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Ouvrir et retourner le fichier
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{template.get_file_name()}"'
            return response

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
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        return SignatureTemplate.objects.filter(user=user)
