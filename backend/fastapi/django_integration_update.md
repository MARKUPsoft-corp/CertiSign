# Mise à jour du Modèle Django pour le Nouveau Workflow de Signature

## Objectif
Associer les informations utilisateur aux documents signés dans le backend Django.

## Modifications du Modèle

Dans votre application Django (probablement dans le fichier `models.py` de l'application qui gère les documents), vous devez mettre à jour le modèle `DocumentSignature` (ou équivalent) :

```python
from django.db import models
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class DocumentSignature(models.Model):
    """
    Modèle de stockage des signatures de documents avec les informations utilisateur.
    """
    document_id = models.UUIDField(primary_key=True, editable=False, verbose_name="ID du document")
    
    # Relation avec l'utilisateur propriétaire (qui a effectué la signature)
    owner = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="signed_documents",
        verbose_name="Propriétaire"
    )
    
    # Métadonnées de signature
    original_hash = models.CharField(max_length=64, verbose_name="Hash du document original")
    signature = models.TextField(verbose_name="Signature cryptographique")
    public_key_pem = models.TextField(verbose_name="Clé publique (PEM)")
    
    # Informations sur le document
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Titre du document")
    
    # Stockage des documents
    original_file = models.FileField(
        upload_to='original_documents', 
        verbose_name="Document original"
    )
    signed_file = models.FileField(
        upload_to='signed_documents', 
        verbose_name="Document signé"
    )
    
    # Métadonnées utilisateur JSON
    user_metadata = models.JSONField(
        blank=True, 
        null=True, 
        verbose_name="Métadonnées utilisateur"
    )
    
    # Champs de suivi
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    class Meta:
        verbose_name = "Signature de document"
        verbose_name_plural = "Signatures de documents"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Document {self.document_id} - {self.title or 'Sans titre'}"
    
    @property
    def user_info(self):
        """
        Retourne les informations utilisateur formatées depuis les métadonnées
        """
        if not self.user_metadata:
            return {}
        
        try:
            if isinstance(self.user_metadata, str):
                return json.loads(self.user_metadata)
            return self.user_metadata
        except:
            return {}
```

## Mise à Jour de l'API Django

Vous devez également mettre à jour la vue API qui reçoit les informations de signature pour gérer les métadonnées utilisateur :

```python
@api_view(['POST'])
@permission_classes([AllowAny])
def store_signature(request):
    """Endpoint spécial pour stocker une signature depuis le microservice."""
    # Vérifier la clé API
    api_key = request.GET.get('api_key')
    if not api_key or api_key != settings.MICROSERVICE_API_KEY:
        return Response({"error": "Clé API invalide"}, status=403)
    
    # Récupérer les données
    document_id = request.POST.get('document_id')
    original_hash = request.POST.get('original_hash')
    signature = request.POST.get('signature')
    public_key_pem = request.POST.get('public_key_pem')
    owner_id = request.POST.get('owner_id')
    title = request.POST.get('title')
    user_metadata = request.POST.get('user_metadata')
    
    # Récupérer les fichiers
    original_file = request.FILES.get('original_file')
    signed_file = request.FILES.get('signed_file')
    
    # Vérifier les données obligatoires
    if not all([document_id, original_hash, signature, public_key_pem, original_file, signed_file]):
        return Response({"error": "Données manquantes"}, status=400)
    
    # Créer l'objet DocumentSignature
    signature_obj = DocumentSignature(
        document_id=document_id,
        original_hash=original_hash,
        signature=signature,
        public_key_pem=public_key_pem,
        title=title,
        user_metadata=user_metadata,
        original_file=original_file,
        signed_file=signed_file
    )
    
    # Associer l'utilisateur si un owner_id est fourni
    if owner_id:
        try:
            user = User.objects.get(id=owner_id)
            signature_obj.owner = user
        except User.DoesNotExist:
            pass  # Continuer sans l'association utilisateur
    
    # Sauvegarder l'objet
    signature_obj.save()
    
    return Response({
        "message": "Signature stockée avec succès",
        "document_id": document_id
    }, status=201)
```

## Mise à Jour de l'Admin Django

Mettez à jour l'administration Django pour afficher les informations utilisateur associées :

```python
@admin.register(DocumentSignature)
class DocumentSignatureAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'title', 'owner_username', 'created_at')
    list_filter = ('created_at', 'owner')
    search_fields = ('document_id', 'title', 'owner__username')
    readonly_fields = ('document_id', 'original_hash', 'signature', 'public_key_pem', 
                      'user_metadata_display', 'created_at', 'updated_at')
    
    def owner_username(self, obj):
        return obj.owner.username if obj.owner else "Non spécifié"
    owner_username.short_description = "Propriétaire"
    
    def user_metadata_display(self, obj):
        if not obj.user_metadata:
            return "Aucune métadonnée"
        
        try:
            metadata = obj.user_info
            html = '<table>'
            for key, value in metadata.items():
                html += f'<tr><th>{key}</th><td>{value}</td></tr>'
            html += '</table>'
            return mark_safe(html)
        except:
            return "Erreur d'affichage des métadonnées"
    user_metadata_display.short_description = "Métadonnées utilisateur"
```

## Migration de la Base de Données

Après avoir mis à jour les modèles, générez et appliquez les migrations :

```bash
python manage.py makemigrations
python manage.py migrate
```

Ces modifications permettront au backend Django de stocker et d'afficher correctement les informations utilisateur associées aux documents signés.
