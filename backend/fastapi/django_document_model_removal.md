# Suppression du Modèle Document Redondant

Dans le cadre de la refonte du workflow de signature, le modèle `Document` est maintenant redondant car toutes les informations sont centralisées dans le modèle `DocumentSignature`. Voici les étapes précises pour le supprimer proprement.

## 1. Mise à jour du modèle DocumentSignature

Avant de supprimer le modèle `Document`, assurez-vous que le modèle `DocumentSignature` possède tous les champs nécessaires. Vérifiez que les informations requises sont déjà présentes dans `DocumentSignature` (ce qui semble être le cas).

## 2. Suppression de la relation dans DocumentSignature

Modifiez le fichier `/home/markupsafe/Documents/CertiSign/backend/django-project/documents/models.py` pour supprimer la relation OneToOne avec Document :

```python
# Supprimer cette relation dans le modèle DocumentSignature
related_document = models.OneToOneField(
    Document, 
    on_delete=models.SET_NULL, 
    null=True, 
    blank=True,
    related_name='signature_info',
    verbose_name=_('Document associé')
)
```

Également, supprimez les références à `related_document` dans la méthode `__str__` :

```python
def __str__(self):
    if self.title:
        return f"Signature - {self.title} ({self.document_id})"
    else:
        return f"Signature - {self.document_id}"
```

## 3. Mettre à jour le modèle DocumentActivity

Ce modèle a une relation avec le modèle Document. Vous avez deux options :
1. Supprimer également ce modèle s'il n'est plus nécessaire
2. Le modifier pour qu'il soit lié à DocumentSignature au lieu de Document

Option 2 - Modification :

```python
class DocumentActivity(models.Model):
    # Remplacer cette relation
    document = models.ForeignKey(
        DocumentSignature,  # Changement ici 
        on_delete=models.CASCADE, 
        related_name='activities',
        verbose_name=_('Document')
    )
    # [...reste du modèle inchangé...]
```

## 4. Supprimer la classe Document

Supprimez entièrement la classe Document du fichier models.py.

## 5. Mettre à jour l'administration Django

Dans le fichier `/home/markupsafe/Documents/CertiSign/backend/django-project/documents/admin.py`, supprimez les références au modèle Document :

```python
# Supprimer ces lignes
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'owner__username')
    readonly_fields = ('id', 'created_at', 'updated_at')
```

## 6. Créer une migration pour supprimer le modèle

Générez et appliquez une migration pour supprimer le modèle :

```bash
cd /home/markupsafe/Documents/CertiSign/backend/django-project
python manage.py makemigrations documents --name remove_document_model
python manage.py migrate
```

## 7. Mise à jour des vues et des formulaires

Mettez à jour les vues et les formulaires qui utilisent le modèle Document pour qu'ils utilisent DocumentSignature à la place.

## 8. Mise à jour des URLs

Assurez-vous que les URLs qui dépendaient des vues associées au modèle Document sont mises à jour ou supprimées.

## 9. Tests et vérification

Testez soigneusement toutes les fonctionnalités après avoir supprimé le modèle pour vous assurer que tout fonctionne correctement.

---

Cette suppression s'aligne parfaitement avec votre nouvelle architecture où les informations de signature, le document et les informations utilisateur sont centralisés dans un seul modèle, simplifiant ainsi le flux de données et améliorant la traçabilité des documents signés.
