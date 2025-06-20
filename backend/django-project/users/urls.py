"""
Configuration des URLs pour l'API des utilisateurs.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Création du routeur pour les ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'organizations', views.OrganizationViewSet)
router.register(r'activities', views.ActivityLogViewSet)

# Import SimpletJWT pour les vues de tokens
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    # Authentification
    path('auth/login/', views.authenticate_user, name='auth-login'),
    path('auth/certificate/', views.authenticate_certificate, name='auth-certificate'),
    path('auth/with-organization/', views.authenticate_with_organization, name='auth-with-organization'),
    path('auth-certificate/', views.auth_certificate_gateway, name='auth-certificate-gateway'),
    path('auth-org-admin/verify/', views.verify_admin_certificate, name='verify-admin-certificate'),
    path('auth-org-admin/authenticate/', views.authenticate_org_admin, name='authenticate-org-admin'),
    
    # Authentification JWT - Utilisation des vues standard de rest_framework_simplejwt
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token-verify/', TokenVerifyView.as_view(), name='token-verify'),
    # Ces vues personnalisées n'existent pas encore, elles sont commentées pour éviter l'erreur
    # path('login/', views.LoginView.as_view(), name='token-login'),
    # path('logout/', views.LogoutView.as_view(), name='token-logout'),
    # path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token-refresh'),
    
    # Utiliser une fonction de vue au lieu d'une vue basée sur classe pour activity-log
    
    # Suivi d'activité
    # En commentaire car la vue basée sur classe n'existe pas encore
    # path('activity-log/', views.ActivityLogCreateView.as_view(), name='activity-log-create'),
    # Utiliser la vue déjà existante pour le moment
    path('activity-log/', views.ActivityLogViewSet.as_view({'post': 'create'}), name='activity-log-create'),
    
    # Organisations
    path('organizations/', views.get_active_organizations, name='active-organizations'),
    
    # Inclure toutes les routes générées par le routeur
    path('', include(router.urls)),
    
    # Points d'entrée spécifiques
    path('me/', views.UserViewSet.as_view({'get': 'me'}), name='current-user'),
] 