from rest_framework import viewsets
from Root.models import *
from ..serializers.userserializer import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None
