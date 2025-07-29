"""
Configuration des URLs du projet CertiSign.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from documents.signature_views import store_signature_public, standard_store_signature_public, standard_get_signature_public
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Personnalisation de l'interface d'administration
admin.site.site_header = "Doc@uthANTIC - Administration"
admin.site.site_title = "Doc@uthANTIC - Administration"
admin.site.index_title = "Administration Doc@uthANTIC"

# Configuration de Swagger/OpenAPI
schema_view = get_schema_view(
   openapi.Info(
      title="CertiSign API",
      default_version='v1',
      description="API pour la gestion des certificats et signatures électroniques",
      terms_of_service="https://www.certisign.com/terms/",
      contact=openapi.Contact(email="contact@certisign.com"),
      license=openapi.License(name="Propriétaire"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/signature-templates/', include('signature_templates.urls')),
    
    # Points d'entrée spéciaux utilisant des vues Django standard (pas REST Framework)
    # pour éviter complètement les middlewares d'authentification JWT
    path('api/public/store_signature/', standard_store_signature_public, name='public-store-signature'),
    path('api/public/get_signature/', standard_get_signature_public, name='public-get-signature'),
    
    # Documentation de l'API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Ajout des URLs pour les médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 