"""
Configuration de l'interface d'administration pour les modèles utilisateur.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Organization, ActivityLog

# Fonction utilitaire pour obtenir l'adresse IP du client
def get_client_ip(request):
    """Récupère l'adresse IP du client."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Administrateur pour les organisations."""
    list_display = ('name', 'registration_number', 'status', 'created_at')
    search_fields = ('name', 'registration_number')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at',)
    actions = ['approve_organizations', 'reject_organizations']
    
    fieldsets = (
        (_('Informations'), {
            'fields': ('name', 'registration_number', 'address')
        }),
        (_('Statut'), {
            'fields': ('status',)
        }),
        (_('Dates'), {
            'fields': ('created_at',)
        }),
    )
    
    def approve_organizations(self, request, queryset):
        """Action pour approuver les organisations sélectionnées."""
        queryset.update(status='active')
        for org in queryset:
            ActivityLog.objects.create(
                user=request.user,
                action_type='org_status_change',
                description=f"Approbation de l'organisation {org.name}",
                ip_address=get_client_ip(request)
            )
    approve_organizations.short_description = _("Approuver les organisations sélectionnées")
    
    def reject_organizations(self, request, queryset):
        """Action pour rejeter les organisations sélectionnées."""
        queryset.update(status='rejected')
        for org in queryset:
            ActivityLog.objects.create(
                user=request.user,
                action_type='org_status_change',
                description=f"Rejet de l'organisation {org.name}",
                ip_address=get_client_ip(request)
            )
    reject_organizations.short_description = _("Rejeter les organisations sélectionnées")

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Administrateur pour le modèle utilisateur personnalisé."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role_with_org', 'status', 'date_joined')
    list_filter = ('role', 'status', 'organization', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'certificate_serial')
    readonly_fields = ('date_joined', 'last_login', 'certificate_serial', 'certificate_dn', 'certificate_expiry')
    actions = ['approve_users', 'reject_users', 'make_admin', 'make_collaborator', 'make_signer', 'make_user']
    
    # Personnalisation des fieldsets
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informations personnelles'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'position')}),
        (_('Organisation et rôle'), {
            'fields': ('organization', 'role'),
            'description': _('Sélectionnez l\'organisation à laquelle appartient l\'utilisateur et définissez son rôle.')
        }),
        (_('Statut du compte'), {
            'fields': ('status', 'is_active'),
            'description': _('Statut « En attente » : compte créé mais non validé. Statut « Actif » : compte validé. Statut « Rejeté » : demande refusée.')
        }),
        (_('Permissions'), {
            'fields': ('is_staff', 'is_superuser'),
            'description': _('Staff : accès à l\'interface d\'administration. Superuser : tous les droits.')
        }),
        (_('Certificat numérique'), {
            'fields': ('certificate_serial', 'certificate_dn', 'certificate_expiry'),
            'description': _('Informations extraites du certificat numérique. Ces champs sont en lecture seule.')
        }),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # Personnalisation du formulaire d'ajout
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        (_('Informations personnelles'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'position')
        }),
        (_('Organisation et rôle'), {
            'fields': ('organization', 'role', 'status')
        }),
    )
    
    def role_with_org(self, obj):
        """Affiche le rôle avec le nom de l'organisation si applicable."""
        if obj.organization:
            return f"{obj.get_role_display()} - {obj.organization.name}"
        return obj.get_role_display()
        
    def delete_model(self, request, obj):
        """
        Supprime proprement un utilisateur en gérant les références orphelines
        aux documents de signature.
        """
        # Suppression des activités de document pour éviter les références
        # orphelines à des DocumentSignature qui n'existent plus
        from documents.models import DocumentActivity
        DocumentActivity.objects.filter(user=obj).delete()
        
        super().delete_model(request, obj)
        
    def delete_queryset(self, request, queryset):
        """
        Supprime proprement plusieurs utilisateurs en gérant les références orphelines
        aux documents de signature.
        """
        # Suppression des activités de document pour éviter les références
        # orphelines à des DocumentSignature qui n'existent plus
        from documents.models import DocumentActivity
        for user in queryset:
            DocumentActivity.objects.filter(user=user).delete()
            
        super().delete_queryset(request, queryset)
    role_with_org.short_description = _('Rôle et Organisation')
    
    def approve_users(self, request, queryset):
        """Action pour approuver les utilisateurs sélectionnés."""
        queryset.update(status='active')
        for user in queryset:
            ActivityLog.objects.create(
                user=request.user,
                action_type='status_change',
                description=f"Approbation de l'utilisateur {user.username}",
                ip_address=get_client_ip(request)
            )
    approve_users.short_description = _("Approuver les utilisateurs sélectionnés")
    
    def reject_users(self, request, queryset):
        """Action pour rejeter les utilisateurs sélectionnés."""
        queryset.update(status='rejected')
        for user in queryset:
            ActivityLog.objects.create(
                user=request.user,
                action_type='status_change',
                description=f"Rejet de l'utilisateur {user.username}",
                ip_address=get_client_ip(request)
            )
    reject_users.short_description = _("Rejeter les utilisateurs sélectionnés")
    
    def make_active(self, request, queryset):
        """Action pour activer les utilisateurs sélectionnés."""
        queryset.update(is_active=True)
        for user in queryset:
            ActivityLog.objects.create(
                user=request.user,
                action_type='user_activation',
                description=f"Activation du compte de {user.username}",
                ip_address=get_client_ip(request)
            )
    make_active.short_description = _("Activer les comptes des utilisateurs sélectionnés")
    
    def make_inactive(self, request, queryset):
        """Action pour désactiver les utilisateurs sélectionnés."""
        queryset.update(is_active=False)
        for user in queryset:
            ActivityLog.objects.create(
                user=request.user,
                action_type='user_deactivation',
                description=f"Désactivation du compte de {user.username}",
                ip_address=get_client_ip(request)
            )
    make_inactive.short_description = _("Désactiver les comptes des utilisateurs sélectionnés")
    
    def make_admin(self, request, queryset):
        """Action pour attribuer le rôle d'administrateur d'organisation."""
        queryset.update(role='admin')
        for user in queryset:
            ActivityLog.objects.create(
                user=request.user,
                action_type='role_change',
                description=f"Attribution du rôle Administrateur d'Organisation à {user.username}",
                ip_address=get_client_ip(request)
            )
    make_admin.short_description = _("Définir comme Administrateur d'Organisation")
    
    def make_collaborator(self, request, queryset):
        """Action pour attribuer le rôle de collaborateur."""
        queryset.update(role='collaborator')
        for user in queryset:
            ActivityLog.objects.create(
                user=request.user,
                action_type='role_change',
                description=f"Attribution du rôle Collaborateur à {user.username}",
                ip_address=get_client_ip(request)
            )
    make_collaborator.short_description = _("Définir comme Collaborateur")
    
    def make_signer(self, request, queryset):
        """Action pour attribuer le rôle de signataire."""
        queryset.update(role='signer')
        for user in queryset:
            ActivityLog.objects.create(
                user=request.user,
                action_type='role_change',
                description=f"Attribution du rôle Signataire à {user.username}",
                ip_address=get_client_ip(request)
            )
    make_signer.short_description = _("Définir comme Signataire")
    
    def make_user(self, request, queryset):
        """Action pour attribuer le rôle d'utilisateur simple."""
        queryset.update(role='user')
        for user in queryset:
            ActivityLog.objects.create(
                user=request.user,
                action_type='role_change',
                description=f"Attribution du rôle Utilisateur Simple à {user.username}",
                ip_address=get_client_ip(request)
            )
    make_user.short_description = _("Définir comme Utilisateur Simple")
    
    def make_active(self, request, queryset):
        """Action pour activer les utilisateurs sélectionnés."""
        queryset.update(is_active=True)
    make_active.short_description = _("Activer les utilisateurs sélectionnés")
    
    def make_inactive(self, request, queryset):
        """Action pour désactiver les utilisateurs sélectionnés."""
        queryset.update(is_active=False)
    make_inactive.short_description = _("Désactiver les utilisateurs sélectionnés")
    
    # Utilise maintenant la fonction globale get_client_ip

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Administrateur pour le journal d'activités."""
    list_display = ('user', 'action_type', 'ip_address', 'timestamp')
    list_filter = ('action_type', 'timestamp', 'user')
    search_fields = ('user__username', 'description', 'ip_address')
    readonly_fields = ('user', 'action_type', 'description', 'ip_address', 'timestamp')
    
    def has_add_permission(self, request):
        """Désactive l'ajout manuel de logs d'activité."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Désactive la modification des logs d'activité."""
        return False 