# images/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, ImageUploadViewSet

router = DefaultRouter()
router.register(r'images', ImageViewSet, basename='image')
router.register(r'upload-image', ImageUploadViewSet, basename='upload-image')

urlpatterns = [
    path('', include(router.urls)),
]
