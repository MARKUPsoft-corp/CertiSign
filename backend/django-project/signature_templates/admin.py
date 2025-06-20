from django.contrib import admin
from django.utils.html import format_html
from .models import SignatureTemplate

@admin.register(SignatureTemplate)
class SignatureTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_display', 'organization_display', 'created_at', 'document_preview', 'qr_size_display')
    list_filter = ('qr_size', 'page_application', 'created_at', 'user__username', 'organization_name')
    search_fields = ('name', 'user__username', 'organization_name')
    readonly_fields = ('created_at', 'updated_at', 'qr_positions_display', 'signature_positions_display', 'document_preview', 'signature_preview')
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'created_at', 'updated_at')
        }),
        ('Utilisateur et organisation', {
            'fields': ('user', 'organization_name', 'user_role', 'organization_role')
        }),
        ('Documents', {
            'fields': ('original_document', 'document_preview', 'preview_document')
        }),
        ('Signature', {
            'fields': ('signature_image', 'signature_preview', 'signature_size')
        }),
        ('Configuration du QR code', {
            'fields': ('qr_size', 'page_application')
        }),
        ('Positions et pages', {
            'fields': ('qr_positions_display', 'signature_positions_display', 'selected_pages'),
            'classes': ('collapse',)
        }),
    )
    
    def user_display(self, obj):
        return obj.user.username
    user_display.short_description = "Utilisateur"
    
    def organization_display(self, obj):
        if obj.organization_name:
            return f"{obj.organization_name} ({obj.organization_role or 'N/A'})"
        return "N/A"
    organization_display.short_description = "Organisation"
    
    def qr_size_display(self, obj):
        sizes = {
            'small': '⬜ Petit',
            'medium': '⬛ Moyen',
            'large': '⬛⬛ Grand'
        }
        return sizes.get(obj.qr_size, obj.qr_size)
    qr_size_display.short_description = "Taille QR"
    
    def qr_positions_display(self, obj):
        if not obj.qr_positions:
            return "Aucune position définie"
        
        html = "<h4>Positions du QR code</h4>"
        html += "<table style='width:100%; border-collapse: collapse;'>"
        html += "<tr><th style='border:1px solid #ddd; padding:8px;'>Page</th><th style='border:1px solid #ddd; padding:8px;'>Position X</th><th style='border:1px solid #ddd; padding:8px;'>Position Y</th></tr>"
        
        if obj.page_application == 'all':
            if 'default' in obj.qr_positions:
                pos = obj.qr_positions['default']
                html += f"<tr><td style='border:1px solid #ddd; padding:8px;'>Toutes</td><td style='border:1px solid #ddd; padding:8px;'>{pos.get('x')}%</td><td style='border:1px solid #ddd; padding:8px;'>{pos.get('y')}%</td></tr>"
        elif obj.page_application == 'individual':
            for page, pos in obj.qr_positions.items():
                html += f"<tr><td style='border:1px solid #ddd; padding:8px;'>{page}</td><td style='border:1px solid #ddd; padding:8px;'>{pos.get('x')}%</td><td style='border:1px solid #ddd; padding:8px;'>{pos.get('y')}%</td></tr>"
        
        html += "</table>"
        return format_html(html)
    qr_positions_display.short_description = "Positions du QR code"
    
    def signature_positions_display(self, obj):
        if not obj.signature_positions:
            return "Aucune signature définie"
        
        html = "<h4>Positions de la signature</h4>"
        html += "<table style='width:100%; border-collapse: collapse;'>"
        html += "<tr><th style='border:1px solid #ddd; padding:8px;'>Page</th><th style='border:1px solid #ddd; padding:8px;'>Position X</th><th style='border:1px solid #ddd; padding:8px;'>Position Y</th></tr>"
        
        if obj.page_application == 'all':
            if 'default' in obj.signature_positions:
                pos = obj.signature_positions['default']
                html += f"<tr><td style='border:1px solid #ddd; padding:8px;'>Toutes</td><td style='border:1px solid #ddd; padding:8px;'>{pos.get('x')}%</td><td style='border:1px solid #ddd; padding:8px;'>{pos.get('y')}%</td></tr>"
        elif obj.page_application == 'individual':
            for page, pos in obj.signature_positions.items():
                html += f"<tr><td style='border:1px solid #ddd; padding:8px;'>{page}</td><td style='border:1px solid #ddd; padding:8px;'>{pos.get('x')}%</td><td style='border:1px solid #ddd; padding:8px;'>{pos.get('y')}%</td></tr>"
        
        html += "</table>"
        return format_html(html)
    signature_positions_display.short_description = "Positions de la signature"
    
    def document_preview(self, obj):
        if obj.preview_document:
            return format_html('<a href="{}" target="_blank"><img src="/static/admin/img/icon-viewlink.svg" alt="Voir"> Voir le document</a>', obj.preview_document.url)
        return "Pas d'aperçu disponible"
    document_preview.short_description = "Aperçu du document"
    
    def signature_preview(self, obj):
        if obj.signature_image:
            return format_html('<img src="{}" alt="Signature" style="max-height: 100px; max-width: 200px;" />', obj.signature_image.url)
        return "Pas de signature"
    signature_preview.short_description = "Aperçu de la signature"
