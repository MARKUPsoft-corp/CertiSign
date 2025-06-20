# Suppression du Modèle Django Obsolète

Suite à la mise à jour du workflow de signature, le modèle qui stockait les documents originaux séparément n'est plus nécessaire. Voici comment procéder à sa suppression proprement.

## 1. Identifier le Modèle à Supprimer

Le modèle à supprimer est probablement `OriginalDocument` ou un modèle similaire qui était utilisé pour stocker les documents avant signature. Ce modèle est maintenant redondant car toutes les informations sont centralisées dans le modèle `DocumentSignature`.

## 2. Créer une Migration pour Supprimer le Modèle

```python
# Dans le fichier de l'application appropriée, créez une migration manuelle
# Par exemple: documents/migrations/0010_remove_original_document.py

from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0009_previous_migration'),  # Remplacez par la dernière migration
    ]

    operations = [
        migrations.DeleteModel(
            name='OriginalDocument',  # Remplacez par le nom réel du modèle
        ),
    ]
```

Alternativement, vous pouvez supprimer le modèle du fichier `models.py` puis exécuter :

```bash
python manage.py makemigrations
```

## 3. Supprimer le Modèle du Fichier models.py

Supprimez la classe du modèle de votre fichier `models.py` :

```python
# Supprimez ce modèle
class OriginalDocument(models.Model):
    document_id = models.UUIDField(primary_key=True, editable=False)
    title = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to='original_documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Document {self.document_id} - {self.title or 'Sans titre'}"
```

## 4. Mettre à Jour l'Admin Django

Supprimez l'enregistrement du modèle dans `admin.py` :

```python
# Supprimez cette partie
@admin.register(OriginalDocument)
class OriginalDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'title', 'uploaded_at')
    search_fields = ('document_id', 'title')
    readonly_fields = ('document_id', 'uploaded_at')
```

## 5. Supprimer les Références au Modèle dans les Vues

Recherchez et supprimez toutes les références au modèle dans vos vues (views.py) ou autres fichiers :

```python
# Supprimez les vues qui utilisent uniquement ce modèle
@api_view(['POST'])
def store_original(request):
    """Endpoint pour stocker un document original."""
    # Tout ce code peut être supprimé
    
@api_view(['POST'])
def store_signed(request):
    """Endpoint pour associer un document signé à un document original."""
    # Tout ce code peut être supprimé
```

## 6. Appliquer la Migration

Appliquez la migration pour supprimer effectivement le modèle de la base de données :

```bash
python manage.py migrate
```

## 7. Nettoyer les URLs

Mettez à jour votre fichier `urls.py` pour supprimer les endpoints associés au modèle :

```python
# Supprimez ces URL
path('api/documents/store_original/', views.store_original, name='store_original'),
path('api/documents/store_signed/', views.store_signed, name='store_signed'),
```

## 8. Vérification

Une fois ces modifications effectuées, vérifiez que l'application fonctionne correctement et que l'interface d'administration Django ne présente pas d'erreurs liées à ce modèle supprimé.

## Note Importante

Assurez-vous de prendre une sauvegarde de la base de données avant d'effectuer ces modifications, surtout si vous avez des données importantes stockées dans le modèle que vous supprimez.

Si vous avez des contraintes de clé étrangère qui dépendent de ce modèle, vous devrez d'abord supprimer ou modifier ces contraintes avant de pouvoir supprimer le modèle.
