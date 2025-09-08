from rest_framework import serializers
from .models import DocumentActivity, DocumentSignature, DocumentQRPosition
from users.models import CustomUser

# La classe DocumentSerializer a été supprimée car le modèle Document est obsolète

class DocumentActivitySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    
    class Meta:
        model = DocumentActivity
        fields = [
            'id', 'document', 'document_title', 'user', 'username',
            'activity_type', 'activity_type_display', 'description',
            'ip_address', 'timestamp', 'metadata'
        ]
        read_only_fields = ['id', 'user', 'username', 'document_title', 'ip_address', 'timestamp', 'activity_type_display']

class DocumentSignatureSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    created_at_display = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M:%S', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    # 🆕 CHAMPS CALCULÉS POUR LES SIGNATURES ÉPHÉMÈRES
    is_valid = serializers.ReadOnlyField()
    validity_status = serializers.ReadOnlyField()
    
    # URLs SFTP personnalisées pour les fichiers
    original_file_url = serializers.SerializerMethodField()
    signed_file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentSignature
        fields = [
            'document_id', 'title', 
            'owner', 'owner_username', 
            'created_at', 'created_at_display', 'original_hash', 
            'signature', 'public_key_pem', 'metadata',
            'organization', 'organization_name', 'signer_role',
            # 🆕 NOUVEAUX CHAMPS POUR SIGNATURES ÉPHÉMÈRES
            'signature_type', 'expiration_date', 'is_valid', 'validity_status',
            # URLs SFTP
            'original_file_url', 'signed_file_url'
        ]
        read_only_fields = ['document_id', 'created_at', 'created_at_display']
        extra_kwargs = {
            'public_key_pem': {'write_only': True},
            'signature': {'write_only': True},
            'original_file': {'write_only': True},
            'signed_file': {'write_only': True}
        }
    
    def get_original_file_url(self, obj):
        """
        Retourne l'URL SFTP pour le fichier original.
        """
        if obj.original_file:
            request = self.context.get('request')
            if request:
                from django.urls import reverse
                try:
                    return request.build_absolute_uri(
                        reverse('document-signature-download', kwargs={'pk': obj.document_id})
                    )
                except:
                    # Fallback si l'URL n'existe pas
                    return f"/api/documents/signatures/{obj.document_id}/download/"
        return None
    
    def get_signed_file_url(self, obj):
        """
        Retourne l'URL SFTP pour le fichier signé.
        """
        if obj.signed_file:
            request = self.context.get('request')
            if request:
                from django.urls import reverse
                try:
                    return request.build_absolute_uri(
                        reverse('document-signature-download', kwargs={'pk': obj.document_id})
                    )
                except:
                    # Fallback si l'URL n'existe pas
                    return f"/api/documents/signatures/{obj.document_id}/download/"
        return None

class DocumentQRPositionSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle DocumentQRPosition.
    """
    collaborator_username = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    # URLs SFTP personnalisées pour les fichiers
    signature_image_url = serializers.SerializerMethodField()
    document_file_url = serializers.SerializerMethodField()
    generated_pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentQRPosition
        fields = [
            'id', 'document_name', 'document_file', 'generated_pdf',
            'qr_x_position', 'qr_y_position', 'qr_size',
            'qr_pages', 'qr_positions', 'qr_mode',
            'signature_image', 'signature_positions', 'signature_size',
            'collaborator', 'organization', 
            'collaborator_username', 'organization_name',
            'status', 'metadata', 'created_at', 'updated_at',
            # URLs SFTP
            'signature_image_url', 'document_file_url', 'generated_pdf_url'
        ]
        read_only_fields = ['id', 'collaborator', 'organization', 'created_at', 'updated_at']
        extra_kwargs = {
            'document_file': {'write_only': True},
            'generated_pdf': {'write_only': True},
            'signature_image': {'write_only': True}  # Masqué pour éviter les URLs /media/
        }
    
    def get_collaborator_username(self, obj):
        return obj.collaborator.username if obj.collaborator else None
    
    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None
    
    def get_signature_image_url(self, obj):
        """
        Retourne l'URL SFTP pour l'image de signature.
        """
        if obj.signature_image:
            request = self.context.get('request')
            if request:
                from django.urls import reverse
                try:
                    return request.build_absolute_uri(
                        reverse('document-qr-position-download-signature-image', kwargs={'pk': obj.id})
                    )
                except:
                    # Fallback si l'URL n'existe pas
                    return f"/api/documents/qr-positions/{obj.id}/download_signature_image/"
        return None
    
    def get_document_file_url(self, obj):
        """
        Retourne l'URL SFTP pour le fichier document.
        """
        if obj.document_file:
            request = self.context.get('request')
            if request:
                from django.urls import reverse
                try:
                    return request.build_absolute_uri(
                        reverse('document-qr-position-download-document', kwargs={'pk': obj.id})
                    )
                except:
                    # Fallback si l'URL n'existe pas
                    return f"/api/documents/qr-positions/{obj.id}/download_document/"
        return None
    
    def get_generated_pdf_url(self, obj):
        """
        Retourne l'URL SFTP pour le PDF généré.
        """
        if obj.generated_pdf:
            request = self.context.get('request')
            if request:
                from django.urls import reverse
                try:
                    return request.build_absolute_uri(
                        reverse('document-qr-position-download-generated-pdf', kwargs={'pk': obj.id})
                    )
                except:
                    # Fallback si l'URL n'existe pas
                    return f"/api/documents/qr-positions/{obj.id}/download_generated_pdf/"
        return None
        
    def validate(self, data):
        """
        Validation personnalisée pour assurer que tous les champs nécessaires sont présents
        et correctement formatés.
        """
        # Pour les mises à jour PATCH, permettre des validations partielles
        is_update = self.instance is not None
        request_method = self.context.get('request', {}).method if self.context.get('request') else 'POST'
        
        # Vérifier la présence du fichier seulement lors de la création
        if not data.get('document_file') and request_method == 'POST' and not is_update:
            raise serializers.ValidationError({"document_file": "Le fichier du document est requis"})
            
        # Vérifier la présence du nom seulement lors de la création ou si explicitement fourni
        if not data.get('document_name') and request_method == 'POST' and not is_update:
            raise serializers.ValidationError({"document_name": "Le nom du document est requis"})
            
        # Vérifier les positions du QR code seulement lors de la création
        if 'qr_x_position' not in data and request_method == 'POST' and not is_update:
            raise serializers.ValidationError({"qr_x_position": "La position X du QR code est requise"})
            
        if 'qr_y_position' not in data and request_method == 'POST' and not is_update:
            raise serializers.ValidationError({"qr_y_position": "La position Y du QR code est requise"})
            
        if 'qr_size' not in data and request_method == 'POST' and not is_update:
            raise serializers.ValidationError({"qr_size": "La taille du QR code est requise"})
                
        # Convertir les chaînes JSON pour qr_positions si nécessaire
        if isinstance(data.get('qr_positions'), str):
            try:
                import json
                data['qr_positions'] = json.loads(data['qr_positions'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({"qr_positions": "Format JSON invalide pour les positions"})
        
        # NOUVEAU: Validation pour signature_positions si présentes
        if isinstance(data.get('signature_positions'), str):
            try:
                import json
                data['signature_positions'] = json.loads(data['signature_positions'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({"signature_positions": "Format JSON invalide pour les positions de signature"})
                
        # Validation des métadonnées (si présentes)
        if isinstance(data.get('metadata'), str):
            try:
                import json
                data['metadata'] = json.loads(data['metadata'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({"metadata": "Format JSON invalide pour les métadonnées"})
                
        return data
