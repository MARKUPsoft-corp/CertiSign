from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SignedDocumentViewSet, DocumentActivityViewSet, DocumentQRPositionViewSet
from .signature_views import DocumentSignatureViewSet, get_signature_by_id, store_signature_public

# Création du routeur pour l'API REST
router = DefaultRouter()
router.register('documents', SignedDocumentViewSet, basename='document')
router.register('activities', DocumentActivityViewSet, basename='document-activity')
router.register('signatures', DocumentSignatureViewSet, basename='document-signature')
router.register(r'qr-positions', DocumentQRPositionViewSet, basename='document-qr-position')

# Routes spécifiques pour les actions personnalisées
store_original = SignedDocumentViewSet.as_view({'post': 'store_original'})
store_signed = SignedDocumentViewSet.as_view({'post': 'store_signed'})
quick_sign = SignedDocumentViewSet.as_view({'post': 'quick_sign'})

# Points d'entrée pour le stockage et la vérification des signatures
store_signature = DocumentSignatureViewSet.as_view({'post': 'store_signature'})

urlpatterns = [
    path('', include(router.urls)),
    
    # Routes directes pour les endpoints de stockage de documents
    path('store_original/', store_original, name='store-original-document'),
    path('store_signed/', store_signed, name='store-signed-document'),
    path('quick_sign/', quick_sign, name='quick-sign-document'),
    
    # Routes pour les signatures
    path('store_signature/', store_signature, name='store-signature'),
    path('signature/<str:document_id>/', get_signature_by_id, name='get-signature-by-id'),
    
    # Route publique spéciale pour le stockage des signatures depuis les microservices
    # Cette route est placée hors du namespace API normal pour éviter les middleware d'authentification
    path('public_signature_storage/', store_signature_public, name='store-signature-public'),
    
    # QR Position specific endpoints
    path('collaborator/<str:user_id>/documents/', DocumentQRPositionViewSet.as_view({'get': 'by_collaborator'}), name='collaborator-documents'),
    
    # Endpoints pour le signataire - Utilisé via router automatiquement
    # path('signer/pending-documents/', DocumentQRPositionViewSet.as_view({'get': 'pending_for_signer'}), name='signer-pending-documents'),
    
    # Endpoint pour le tableau de bord administrateur
    path('admin/dashboard/', DocumentQRPositionViewSet.as_view({'get': 'admin_dashboard'}), name='admin-dashboard'),
]
