from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField
from Root.models import auto_admin_register

@auto_admin_register()
class Spare(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    machineId = models.ForeignKey('Root.Machine', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255, null=False)
    number = models.IntegerField(null=False)
    quantity = models.IntegerField(null=False)
    description = models.TextField(blank=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
@auto_admin_register()
class spareAlert(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    spareId = models.ForeignKey(Spare, on_delete=models.CASCADE, related_name='spare_alert_id', null=False)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
