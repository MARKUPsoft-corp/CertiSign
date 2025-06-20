"""
Modèles pour la gestion des utilisateurs dans CertiSign.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Organization(models.Model):
    """
    Modèle représentant une organisation ou entreprise.
    """
    ORGANIZATION_STATUS = (
        ('pending', _('En attente')),
        ('active', _('Active')),
        ('rejected', _('Rejetée')),
    )
    
    name = models.CharField(_("Nom"), max_length=255)
    registration_number = models.CharField(_("Numéro d'immatriculation"), max_length=100, unique=True)
    email = models.EmailField(_("Email de contact"), max_length=255, blank=True, null=True)
    address = models.TextField(_("Adresse"), blank=True, null=True)
    status = models.CharField(_("Statut"), max_length=20, choices=ORGANIZATION_STATUS, default='pending')
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Organisation")
        verbose_name_plural = _("Organisations")
        ordering = ['name']
    
    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    """
    Modèle utilisateur personnalisé avec des champs supplémentaires
    pour gérer les certificats et les rôles.
    """
    USER_ROLES = (
        ('superadmin', _('Super Administrateur')),
        ('admin', _('Administrateur d\'Organisation')),
        ('collaborator', _('Collaborateur')),
        ('signer', _('Signataire')),
        ('user', _('Utilisateur Simple')),
    )
    
    USER_STATUS = (
        ('pending', _('En attente')),
        ('active', _('Actif')),
        ('rejected', _('Rejeté')),
    )
    
    email = models.EmailField(_("Adresse email"), unique=True)
    role = models.CharField(_("Rôle"), max_length=20, choices=USER_ROLES, default='user')
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='members',
        verbose_name=_("Organisation")
    )
    status = models.CharField(_("Statut"), max_length=20, choices=USER_STATUS, default='pending')
    
    # Champs liés au certificat numérique
    certificate_serial = models.CharField(
        _("Numéro de série du certificat"), 
        max_length=255, 
        null=True, 
        blank=True, 
        unique=True
    )
    certificate_dn = models.TextField(_("Distinguished Name (DN)"), null=True, blank=True)
    certificate_expiry = models.DateField(_("Date d'expiration du certificat"), null=True, blank=True)
    
    # Informations supplémentaires
    phone_number = models.CharField(_("Numéro de téléphone"), max_length=20, blank=True, null=True)
    position = models.CharField(_("Poste/Fonction"), max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role in ['admin', 'superadmin']
    
    @property
    def is_superadmin(self):
        return self.role == 'superadmin'
        
    @property
    def is_org_admin(self):
        return self.role == 'admin'
    
    @property
    def is_collaborator(self):
        return self.role == 'collaborator'
    
    @property
    def is_signer(self):
        return self.role == 'signer'
    
    @property
    def is_simple_user(self):
        return self.role == 'user'
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
        
    @property
    def role_display_with_org(self):
        if self.organization:
            return f"{self.get_role_display()} - {self.organization.name}"
        return self.get_role_display()

class ActivityLog(models.Model):
    """
    Modèle pour enregistrer les activités des utilisateurs.
    """
    ACTION_TYPES = (
        ('login', _('Connexion')),
        ('logout', _('Déconnexion')),
        ('sign', _('Signature de document')),
        ('verify', _('Vérification de document')),
        ('upload', _('Téléversement de document')),
        ('status_change', _('Changement de statut')),
    )
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='activities',
        verbose_name=_("Utilisateur")
    )
    action_type = models.CharField(_("Type d'action"), max_length=20, choices=ACTION_TYPES)
    description = models.TextField(_("Description"))
    ip_address = models.GenericIPAddressField(_("Adresse IP"), null=True, blank=True)
    timestamp = models.DateTimeField(_("Horodatage"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Journal d'activité")
        verbose_name_plural = _("Journal d'activités")
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} - {self.timestamp}" 