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
    
    class Meta:
        model = DocumentSignature
        fields = [
            'document_id', 'title', 
            'owner', 'owner_username', 'original_file', 'signed_file',
            'created_at', 'created_at_display', 'original_hash', 
            'signature', 'public_key_pem', 'metadata',
            'organization', 'organization_name', 'signer_role'
        ]
        read_only_fields = ['document_id', 'created_at', 'created_at_display']
        extra_kwargs = {
            'public_key_pem': {'write_only': True},
            'signature': {'write_only': True}
        }

class DocumentQRPositionSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle DocumentQRPosition.
    """
    collaborator_username = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentQRPosition
        fields = [
            'id', 'document_name', 'document_file', 
            'qr_x_position', 'qr_y_position', 'qr_size',
            'qr_pages', 'qr_positions', 'qr_mode',
            'collaborator', 'organization', 
            'collaborator_username', 'organization_name',
            'status', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'collaborator', 'organization', 'created_at', 'updated_at']
    
    def get_collaborator_username(self, obj):
        return obj.collaborator.username if obj.collaborator else None
    
    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None
        
    def validate(self, data):
        """
        Validation personnalisée pour assurer que tous les champs nécessaires sont présents
        et correctement formatés.
        """
        # Vérifier la présence du fichier
        if not data.get('document_file') and self.context['request'].method == 'POST':
            raise serializers.ValidationError({"document_file": "Le fichier du document est requis"})
            
        # Vérifier la présence du nom
        if not data.get('document_name'):
            raise serializers.ValidationError({"document_name": "Le nom du document est requis"})
            
        # Vérifier les positions du QR code
        if 'qr_x_position' not in data:
            raise serializers.ValidationError({"qr_x_position": "La position X du QR code est requise"})
            
        if 'qr_y_position' not in data:
            raise serializers.ValidationError({"qr_y_position": "La position Y du QR code est requise"})
            
        if 'qr_size' not in data:
            raise serializers.ValidationError({"qr_size": "La taille du QR code est requise"})
                
        # Convertir les chaînes JSON pour qr_positions si nécessaire
        if isinstance(data.get('qr_positions'), str):
            try:
                import json
                data['qr_positions'] = json.loads(data['qr_positions'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({"qr_positions": "Format JSON invalide pour les positions"})
                
        # Validation des métadonnées (si présentes)
        if isinstance(data.get('metadata'), str):
            try:
                import json
                data['metadata'] = json.loads(data['metadata'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({"metadata": "Format JSON invalide pour les métadonnées"})
                
        return data
