from rest_framework import viewsets, status
from .serializers import ImageSerializer, ImageUploadSerializer
from rest_framework.response import Response
from rest_framework import permissions
from .models import Image
from rest_framework.parsers import MultiPartParser, FormParser

# Image viewset
class ImageViewSet(viewsets.ModelViewSet):
    """
       ViewSet for viewing and editing Image instances.
       
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [permissions.AllowAny]
    

# Image upload viewset
class ImageUploadViewSet(viewsets.ModelViewSet):
    """
       ViewSet for handling image upload functionality.
       
    """
    queryset = Image.objects.all()
    serializer_class = ImageUploadSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
