from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.SignatureTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('templates-list/', views.SignatureTemplateList.as_view(), name='template-list'),
    path('templates-detail/<int:pk>/', views.SignatureTemplateDetail.as_view(), name='template-detail'),
] 