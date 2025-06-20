"""
Serializers pour l'API REST des utilisateurs.
"""

from rest_framework import serializers
from .models import CustomUser, Organization, ActivityLog

class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer pour les organisations."""
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'registration_number', 'address', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les utilisateurs."""
    
    organization_name = serializers.CharField(write_only=True, required=False)
    organization_details = OrganizationSerializer(source='organization', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password', 
            'first_name', 'last_name', 'full_name',
            'role', 'status', 'is_active',
            'certificate_serial', 'certificate_dn', 'certificate_expiry',
            'phone_number', 'position',
            'organization', 'organization_name', 'organization_details',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_full_name(self, obj):
        """Obtient le nom complet de l'utilisateur."""
        return obj.full_name
    
    def create(self, validated_data):
        """
        Crée un nouvel utilisateur avec les données validées.
        Gère les mots de passe hashés et la création d'organisation.
        """
        organization_name = validated_data.pop('organization_name', None)
        password = validated_data.pop('password', None)
        
        # Créer ou récupérer l'organisation si un nom est fourni
        if organization_name:
            organization, created = Organization.objects.get_or_create(
                name=organization_name,
                defaults={'registration_number': f'ORG-{organization_name[:8]}'}
            )
            validated_data['organization'] = organization
        
        # Créer l'utilisateur
        user = CustomUser.objects.create(**validated_data)
        
        # Définir le mot de passe
        if password:
            user.set_password(password)
            user.save()
            
        # Stocker l'utilisateur qui a créé ce compte (pour le logging)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user._creator = request.user
            
        return user
    
    def update(self, instance, validated_data):
        """
        Met à jour un utilisateur existant.
        Gère les mots de passe et la mise à jour/création d'organisation.
        """
        # Gérer le mot de passe séparément
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # Gérer l'organisation
        organization_name = validated_data.pop('organization_name', None)
        if organization_name:
            organization, created = Organization.objects.get_or_create(
                name=organization_name,
                defaults={'registration_number': f'ORG-{organization_name[:8]}'}
            )
            validated_data['organization'] = organization
        
        # Mettre à jour les autres champs
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer pour les journaux d'activité."""
    
    user_username = serializers.ReadOnlyField(source='user.username')
    action_type_display = serializers.ReadOnlyField(source='get_action_type_display')
    
    class Meta:
        model = ActivityLog
        fields = [
            'id', 'user', 'user_username', 
            'action_type', 'action_type_display',
            'description', 'ip_address', 'timestamp'
        ]
        read_only_fields = fields 