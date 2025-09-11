from rest_framework import serializers
from .models import SignatureTemplate
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')

class SignatureTemplateSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    original_document_name = serializers.SerializerMethodField()
    
    # Remplacer les URLs media par des endpoints SFTP
    original_document = serializers.SerializerMethodField()
    signature_image = serializers.SerializerMethodField()
    preview_document = serializers.SerializerMethodField()
    
    class Meta:
        model = SignatureTemplate
        fields = [
            'id', 'name', 'created_at', 'updated_at',
            'user', 'user_details', 'organization_name', 'user_role', 'organization_role',
            'original_document', 'original_document_name', 'signature_image', 'preview_document',
            'qr_size', 'page_application', 'qr_positions', 'signature_positions',
            'selected_pages', 'signature_size'
        ]
        read_only_fields = ('created_at', 'updated_at')
    
    def get_original_document_name(self, obj):
        if obj.original_document:
            return obj.get_file_name()
        return None
    
    def get_original_document(self, obj):
        """Retourner l'endpoint SFTP absolu pour le document original"""
        if obj.original_document:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/api/signature-templates/templates/{obj.id}/download_original/")
            return f"/api/signature-templates/templates/{obj.id}/download_original/"
        return None
    
    def get_signature_image(self, obj):
        """Retourner l'endpoint SFTP absolu pour l'image de signature"""
        if obj.signature_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/api/signature-templates/templates/{obj.id}/download_signature_image/")
            return f"/api/signature-templates/templates/{obj.id}/download_signature_image/"
        return None
    
    def get_preview_document(self, obj):
        """Retourner l'endpoint SFTP absolu pour l'aperçu du document (affichage dans iframe)"""
        if obj.preview_document:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/api/signature-templates/templates/{obj.id}/preview_document/")
            return f"/api/signature-templates/templates/{obj.id}/preview_document/"
        return None
    
    def create(self, validated_data):
        # Assurez-vous que l'utilisateur actuel est défini comme propriétaire
        user = self.context['request'].user
        
        # Récupérer les informations sur l'organisation de l'utilisateur si disponibles
        if user.organization:
            validated_data['organization_name'] = user.organization.name
            validated_data['organization_role'] = getattr(user, 'role', 'collaborator')
        
        validated_data['user_role'] = getattr(user, 'role', 'user')
        
        # Extraire les fichiers des validated_data pour les traiter séparément
        files_data = {}
        if 'original_document' in validated_data:
            files_data['original_document'] = validated_data.pop('original_document')
        if 'signature_image' in validated_data:
            files_data['signature_image'] = validated_data.pop('signature_image')
        if 'preview_document' in validated_data:
            files_data['preview_document'] = validated_data.pop('preview_document')
        
        # Créer l'instance AVEC l'utilisateur mais SANS les fichiers d'abord
        validated_data['user'] = user
        instance = SignatureTemplate.objects.create(**validated_data)
        
        print(f"✅ [DEBUG] Template créé avec ID {instance.id} et user_id {instance.user.id}")
        
        # Maintenant traiter les fichiers un par un
        if 'original_document' in files_data:
            instance.original_document = files_data['original_document']
            print(f"✅ [DEBUG] Document original assigné: {instance.original_document.name}")
        
        if 'signature_image' in files_data:
            instance.signature_image = files_data['signature_image']
            print(f"✅ [DEBUG] Image de signature assignée: {instance.signature_image.name}")
        
        if 'preview_document' in files_data:
            instance.preview_document = files_data['preview_document']
            print(f"✅ [DEBUG] Document de prévisualisation assigné: {instance.preview_document.name}")
        
        # Sauvegarder avec les fichiers
        if files_data:
            instance.save()
            print(f"✅ [DEBUG] Template sauvegardé avec les fichiers")
        
        return instance
    
    def update(self, instance, validated_data):
        print(f"🔍 [DEBUG BACKEND] Mise à jour du template {instance.id}")
        print(f"🔍 [DEBUG BACKEND] Données reçues: {list(validated_data.keys())}")
        
        # Vérifier si un nouveau preview_document est fourni
        if 'preview_document' in validated_data:
            old_preview = instance.preview_document.name if instance.preview_document else None
            print(f"🔍 [DEBUG BACKEND] Ancien preview: {old_preview}")
            print(f"🔍 [DEBUG BACKEND] Nouveau preview: {validated_data['preview_document'].name}")
            
            # Supprimer l'ancien fichier si il existe
            if instance.preview_document:
                try:
                    instance.preview_document.delete(save=False)
                    print(f"✅ [DEBUG BACKEND] Ancien fichier supprimé")
                except Exception as e:
                    print(f"⚠️ [DEBUG BACKEND] Erreur lors de la suppression: {e}")
        
        # Mettre à jour l'instance
        updated_instance = super().update(instance, validated_data)
        
        print(f"✅ [DEBUG BACKEND] Template mis à jour avec succès")
        print(f"✅ [DEBUG BACKEND] Nouveau preview: {updated_instance.preview_document.name if updated_instance.preview_document else None}")
        
        return updated_instance

class SignatureTemplateListSerializer(serializers.ModelSerializer):
    preview_document = serializers.SerializerMethodField()
    """Sérialiseur pour la liste des templates (version allégée)"""
    class Meta:
        model = SignatureTemplate
        fields = ('id', 'name', 'created_at', 'qr_size', 'page_application', 'organization_name', 'preview_document')


    def get_preview_document(self, obj):
        """Retourner l'endpoint SFTP absolu pour l'aperçu du document (affichage dans iframe)"""
        if obj.preview_document:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/api/signature-templates/templates/{obj.id}/preview_document/")
            return f"/api/signature-templates/templates/{obj.id}/preview_document/"
        return None

class SignatureTemplateCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création d'un template avec plus de validation"""
    class Meta:
        model = SignatureTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'user')
    
    def validate_original_document(self, value):
        # Vérifier que le fichier est un PDF
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Le document original doit être un fichier PDF.")
        return value
    
    def create(self, validated_data):
        # Assurez-vous que l'utilisateur actuel est défini comme propriétaire
        user = self.context['request'].user
        
        # Récupérer les informations sur l'organisation de l'utilisateur si disponibles
        if user.organization:
            validated_data['organization_name'] = user.organization.name
            validated_data['organization_role'] = getattr(user, 'role', 'collaborator')
        
        validated_data['user_role'] = getattr(user, 'role', 'user')
        
        # Extraire les fichiers des validated_data pour les traiter séparément
        files_data = {}
        if 'original_document' in validated_data:
            files_data['original_document'] = validated_data.pop('original_document')
        if 'signature_image' in validated_data:
            files_data['signature_image'] = validated_data.pop('signature_image')
        if 'preview_document' in validated_data:
            files_data['preview_document'] = validated_data.pop('preview_document')
        
        # Créer l'instance AVEC l'utilisateur mais SANS les fichiers d'abord
        validated_data['user'] = user
        instance = SignatureTemplate.objects.create(**validated_data)
        
        print(f"✅ [DEBUG CREATE] Template créé avec ID {instance.id} et user_id {instance.user.id}")
        
        # Maintenant traiter les fichiers un par un
        if 'original_document' in files_data:
            instance.original_document = files_data['original_document']
            print(f"✅ [DEBUG CREATE] Document original assigné: {instance.original_document.name}")
        
        if 'signature_image' in files_data:
            instance.signature_image = files_data['signature_image']
            print(f"✅ [DEBUG CREATE] Image de signature assignée: {instance.signature_image.name}")
        
        if 'preview_document' in files_data:
            instance.preview_document = files_data['preview_document']
            print(f"✅ [DEBUG CREATE] Document de prévisualisation assigné: {instance.preview_document.name}")
        
        # Sauvegarder avec les fichiers
        if files_data:
            instance.save()
            print(f"✅ [DEBUG CREATE] Template sauvegardé avec les fichiers")
        
        return instance
