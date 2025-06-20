from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import DocumentActivity, DocumentSignature, DocumentQRPosition

class DocumentActivityAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les activités sur les documents.
    """
    list_display = ('document', 'user', 'activity_type_display', 'timestamp_display', 'ip_address')
    list_filter = ('activity_type', 'timestamp', 'user')
    search_fields = ('document__title', 'user__username', 'user__email', 'description')
    readonly_fields = ('document', 'user', 'activity_type', 'description', 'ip_address', 'timestamp', 'metadata')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        (_('Informations de base'), {
            'fields': ('document', 'user', 'activity_type', 'description')
        }),
        (_('Informations techniques'), {
            'fields': ('ip_address', 'timestamp'),
            'classes': ('collapse',)
        }),
        (_('Métadonnées'), {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )
    
    def activity_type_display(self, obj):
        """Affiche le type d'activité avec une couleur spécifique."""
        activity_colors = {
            'created': '#17a2b8',  # info
            'viewed': '#6c757d',   # secondary
            'modified': '#007bff', # primary
            'signed': '#28a745',   # success
            'downloaded': '#ffc107', # warning
        }
        color = activity_colors.get(obj.activity_type, 'black')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', 
                          color, obj.get_activity_type_display())
    activity_type_display.short_description = _('Type d\'activité')
    
    def timestamp_display(self, obj):
        """Format de l'horodatage."""
        return obj.timestamp.strftime('%d/%m/%Y %H:%M:%S')
    timestamp_display.short_description = _('Date et heure')

class DocumentSignatureAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les signatures de documents.
    """
    list_display = ('document_id', 'title_display', 'owner_display', 'organization_display', 'signer_role_display', 'created_at_display', 'has_original', 'has_signed')
    list_filter = ('created_at', 'owner', 'organization', 'signer_role')
    search_fields = ('document_id', 'title', 'original_hash', 'owner__username', 'organization__name', 'signer_role')
    readonly_fields = ('document_id', 'created_at', 'display_original_file', 'display_signed_file',
                        'original_hash', 'signature_preview', 'public_key_preview')
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': ('document_id', 'title', 'owner', 'organization', 'signer_role', 'created_at')
        }),
        (_('Fichiers'), {
            'fields': ('display_original_file', 'display_signed_file'),
        }),
        (_('Informations cryptographiques'), {
            'fields': ('original_hash', 'signature_preview', 'public_key_preview'),
            'classes': ('collapse',),
        }),
        (_('Métadonnées'), {
            'fields': ('metadata',),
            'classes': ('collapse',),
        })
    )
    
    def title_display(self, obj):
        """Affiche le titre du document."""
        if obj.title:
            return obj.title
        return f"Document {obj.document_id}"
    title_display.short_description = _('Titre')
    
    def owner_display(self, obj):
        """Affiche le propriétaire de la signature."""
        if obj.owner:
            return obj.owner.username
        return "-"
    owner_display.short_description = _('Propriétaire')
    
    def organization_display(self, obj):
        """Affiche l'organisation associée à la signature."""
        if obj.organization:
            return obj.organization.name
        return "-"
    organization_display.short_description = _('Organisation')
    
    def signer_role_display(self, obj):
        """Affiche le rôle du signataire."""
        if obj.signer_role:
            return obj.signer_role
        return "-"
    signer_role_display.short_description = _('Rôle du signataire')
    
    def created_at_display(self, obj):
        """Format de la date de création."""
        return obj.created_at.strftime('%d/%m/%Y %H:%M:%S')
    created_at_display.short_description = _('Date de création')
    
    def has_original(self, obj):
        """Indique si le fichier original est disponible."""
        return bool(obj.original_file)
    has_original.boolean = True
    has_original.short_description = _('Original')
    
    def has_signed(self, obj):
        """Indique si le fichier signé est disponible."""
        return bool(obj.signed_file)
    has_signed.boolean = True
    has_signed.short_description = _('Signé')
    
    def display_original_file(self, obj):
        """Affiche un lien pour prévisualiser le document original."""
        if obj.original_file:
            return format_html('<a href="{}" target="_blank">Prévisualiser</a>', obj.original_file.url)
        return "-"
    display_original_file.short_description = _('Document original')
    
    def display_signed_file(self, obj):
        """Affiche un lien pour prévisualiser le document signé."""
        if obj.signed_file:
            return format_html('<a href="{}" target="_blank">Prévisualiser</a>', obj.signed_file.url)
        return "-"
    display_signed_file.short_description = _('Document signé')
    
    def signature_preview(self, obj):
        """Affiche un aperçu de la signature."""
        if obj.signature:
            sig_excerpt = f"{obj.signature[:25]}...{obj.signature[-25:]}" if len(obj.signature) > 60 else obj.signature
            return format_html('<code>{}</code><br><small>(signature complète masquée pour sécurité)</small>', sig_excerpt)
        return "-"
    signature_preview.short_description = _('Signature')
    
    def public_key_preview(self, obj):
        """Affiche un aperçu de la clé publique."""
        if obj.public_key_pem:
            lines = obj.public_key_pem.strip().split('\n')
            if len(lines) > 5:
                preview = '\n'.join([lines[0], lines[1], '...', lines[-2], lines[-1]])
            else:
                preview = obj.public_key_pem
            return format_html('<pre style="max-height: 150px; overflow-y: auto;">{}</pre>', preview)
        return "-"
    public_key_preview.short_description = _('Clé publique')

@admin.register(DocumentQRPosition)
class DocumentQRPositionAdmin(admin.ModelAdmin):
    """
    Administration des positions de QR code sur les documents.
    """
    list_display = ('document_name', 'collaborator', 'organization', 'status', 'created_at')
    list_filter = ('status', 'collaborator', 'organization', 'created_at')
    search_fields = ('document_name', 'collaborator__username', 'organization__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Document', {
            'fields': ('id', 'document_name', 'document_file', 'status')
        }),
        ('Positionnement QR', {
            'fields': ('qr_x_position', 'qr_y_position', 'qr_size', 'qr_pages', 'qr_positions', 'qr_mode')
        }),
        ('Relations', {
            'fields': ('collaborator', 'organization')
        }),
        ('Métadonnées', {
            'fields': ('metadata', 'created_at', 'updated_at')
        }),
    )

# Enregistrement des modèles
admin.site.register(DocumentActivity, DocumentActivityAdmin)
admin.site.register(DocumentSignature, DocumentSignatureAdmin)
