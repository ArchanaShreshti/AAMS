from Root.models import Customer
from rest_framework import viewsets
from ..serializers.customerserializer import CustomerSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    pagination_class = None
