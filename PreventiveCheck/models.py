from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField
from Root.models import auto_admin_register

@auto_admin_register()
class PreventiveCheck(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    machineId = models.ForeignKey('Root.Machine', on_delete=models.CASCADE, null=False)
    customerId = models.ForeignKey('Root.Customer', on_delete=models.CASCADE, null=False)
    info = models.JSONField(null=False)
    type = models.CharField(max_length=255, null=False)
    thermography = models.CharField(max_length=255, blank=True)
    image = models.JSONField()

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type

@auto_admin_register()
class preventiveCheckAlert(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    preventiveCheckId = models.ForeignKey(PreventiveCheck, on_delete=models.CASCADE, related_name='preventive_check_alert_id')
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
