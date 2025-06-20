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
    
    class Meta:
        model = SignatureTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_original_document_name(self, obj):
        if obj.original_document:
            return obj.get_file_name()
        return None
    
    def create(self, validated_data):
        # Assurez-vous que l'utilisateur actuel est défini comme propriétaire
        user = self.context['request'].user
        validated_data['user'] = user
        
        return super().create(validated_data)

class SignatureTemplateListSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la liste des templates (version allégée)"""
    class Meta:
        model = SignatureTemplate
        fields = ('id', 'name', 'created_at', 'qr_size', 'page_application', 'organization_name')

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
    
    def validate_signature_image(self, value):
        # Vérifier que l'image est dans un format accepté
        valid_extensions = ['.jpg', '.jpeg', '.png']
        ext = '.' + value.name.split('.')[-1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError("L'image de signature doit être au format JPG ou PNG.")
        return value
    
    def create(self, validated_data):
        # Assurez-vous que l'utilisateur actuel est défini comme propriétaire
        user = self.context['request'].user
        validated_data['user'] = user
        
        # Récupérer les informations sur l'organisation de l'utilisateur si disponibles
        if hasattr(user, 'profile') and user.profile.organization:
            validated_data['organization_name'] = user.profile.organization.name
            validated_data['organization_role'] = user.profile.role
        
        validated_data['user_role'] = getattr(user, 'role', 'user')
        
        return super().create(validated_data) 