from rest_framework import viewsets
from Root.models import *
from ..serializers.userserializer import UserSerializer
from ..serializers.baseserializers import ObjectIdField

class UserViewSet(viewsets.ModelViewSet):
    id = ObjectIdField(read_only=True)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        customer_id = self.request.data.get('customerId')
        if customer_id:
            try:
                customer = Customer.objects.get(id=ObjectId(customer_id))
                serializer.save(customerId=customer)
            except Customer.DoesNotExist:
                raise ValidationError("Invalid customerId")
        else:
            serializer.save()