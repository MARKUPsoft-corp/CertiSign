from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django.core.files.base import ContentFile
from users.models import CustomUser

class DocumentActivity(models.Model):
    """
    Modèle pour enregistrer les activités spécifiques liées aux documents signés
    """
    ACTIVITY_TYPES = (
        ('created', _('Création')),
        ('viewed', _('Consultation')),
        ('modified', _('Modification')),
        ('signed', _('Signature')),
        ('downloaded', _('Téléchargement')),
    )
    
    document = models.ForeignKey(
        'DocumentSignature', 
        on_delete=models.CASCADE, 
        related_name='activities',
        verbose_name=_('Document signé')
    )
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='document_activities',
        verbose_name=_('Utilisateur')
    )
    activity_type = models.CharField(_('Type d\'activité'), max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(_('Description'))
    ip_address = models.GenericIPAddressField(_('Adresse IP'), null=True, blank=True)
    timestamp = models.DateTimeField(_('Horodatage'), auto_now_add=True)
    metadata = models.JSONField(_('Métadonnées'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Activité de document')
        verbose_name_plural = _('Activités de documents')
        ordering = ['-timestamp']
    
    def __str__(self):
        try:
            document_title = self.document.title if self.document else "Document inconnu"
        except DocumentSignature.DoesNotExist:
            document_title = "Document supprimé"
        
        try:
            username = self.user.username if self.user else "Utilisateur inconnu"
        except:
            username = "Utilisateur supprimé"
            
        return f"{document_title} - {self.get_activity_type_display()} - {username}"

class DocumentSignature(models.Model):
    """
    Modèle pour stocker les informations de signature d'un document.
    Ce modèle est conçu pour l'approche où seul l'ID du document est inclus dans le QR code,
    et toutes les informations cryptographiques sont stockées en base de données.
    """
    # Identifiant du document (celui qui apparaît dans le QR code)
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('ID du document'))
    
    # Métadonnées du document
    title = models.CharField(_('Titre du document'), max_length=255, blank=True, null=True)
    
    # Propriétaire du document
    owner = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='signed_documents',
        verbose_name=_('Propriétaire')
    )
    
    # Organisation et rôle de la personne qui a signé
    organization = models.ForeignKey(
        'users.Organization', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='organization_documents',
        verbose_name=_('Organisation')
    )
    signer_role = models.CharField(_('Rôle du signataire'), max_length=100, blank=True, null=True)
    
    # Fichiers du document
    original_file = models.FileField(_('Fichier original'), upload_to='signatures/original/')
    signed_file = models.FileField(_('Fichier signé'), upload_to='signatures/signed/')
    
    # Dates
    created_at = models.DateTimeField(_('Date de création'), auto_now_add=True)
    
    # Données cryptographiques
    original_hash = models.CharField(_('Hash du document original'), max_length=255, default='', blank=True)
    signature = models.TextField(_('Signature'), help_text=_('Signature en base64'), default='', blank=True)
    public_key_pem = models.TextField(_('Clé publique PEM'), default='', blank=True)
    
    # Métadonnées supplémentaires (facultatif)
    metadata = models.JSONField(_('Métadonnées'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Signature de document')
        verbose_name_plural = _('Signatures de documents')
        ordering = ['-created_at']
    
    def __str__(self):
        if self.title:
            return f"Signature - {self.title} ({self.document_id})"
        else:
            return f"Signature - {self.document_id}"
    
    @classmethod
    def create_from_signature_data(cls, document_id, original_hash, signature, public_key_pem, 
                                  document_file_data, signed_file_data, owner=None, title=None,
                                  organization=None, signer_role=None):
        """
        Méthode de classe utilitaire pour créer une signature à partir des données brutes.
        """
        obj = cls(
            document_id=document_id,
            original_hash=original_hash,
            signature=signature,
            public_key_pem=public_key_pem,
            title=title,
            owner=owner,
            organization=organization,
            signer_role=signer_role
        )
        
        # Ajouter les fichiers
        obj.original_file.save(f"{document_id}_original.pdf", ContentFile(document_file_data), save=False)
        obj.signed_file.save(f"{document_id}_signed.pdf", ContentFile(signed_file_data), save=False)
        
        # Enregistrer l'objet
        obj.save()
        return obj

class DocumentQRPosition(models.Model):
    """
    Modèle pour stocker les informations de positionnement du QR code sur un document.
    Créé pour le workflow du collaborateur lors de la préparation des documents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('ID'))
    
    # Fichier document
    document_file = models.FileField(_('Fichier document'), upload_to='documents/prepared/')
    document_name = models.CharField(_('Nom du document'), max_length=255)
    
    # Informations de positionnement du QR code
    qr_x_position = models.FloatField(_('Position X du QR code'))
    qr_y_position = models.FloatField(_('Position Y du QR code'))
    qr_size = models.CharField(_('Taille du QR code'), max_length=20, default='medium')
    qr_pages = models.CharField(_('Pages avec QR code'), max_length=255, default='all')
    qr_positions = models.JSONField(_('Positions du QR code par page'), default=dict, null=True, blank=True)
    qr_mode = models.CharField(_('Mode de positionnement'), max_length=20, default='standard')

    # NOUVEAU: Informations de signature
    signature_image = models.FileField(_('Image de signature'), upload_to='signatures/images/', null=True, blank=True)
    signature_positions = models.JSONField(_('Positions de la signature par page'), default=dict, null=True, blank=True)
    signature_size = models.IntegerField(_('Taille de la signature en %'), default=50, null=True, blank=True)
    
    # Références aux utilisateurs et organisation
    collaborator = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='prepared_documents',
        verbose_name=_('Collaborateur')
    )
    organization = models.ForeignKey(
        'users.Organization', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='prepared_documents',
        verbose_name=_('Organisation')
    )
    
    # Statut et métadonnées
    status = models.CharField(_('Statut'), max_length=20, default='draft', 
                            choices=(
                                ('draft', _('Brouillon')),
                                ('pending_signature', _('En attente de signature')),
                                ('signed', _('Signé')),
                                ('rejected', _('Rejeté')),
                            ))
    metadata = models.JSONField(_('Métadonnées'), null=True, blank=True)
    
    # Dates
    created_at = models.DateTimeField(_('Date de création'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Date de mise à jour'), auto_now=True)
    
    class Meta:
        verbose_name = _('Position QR de document')
        verbose_name_plural = _('Positions QR de documents')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"QR Position - {self.document_name} ({self.id})"
