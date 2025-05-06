from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField
from Root.models import auto_admin_register

@auto_admin_register()
class Safety(models.Model):
    id=ObjectIdAutoField(primary_key=True)
    sensorId = models.ForeignKey('Vibration.Sensor', on_delete=models.CASCADE, null=False)
    image = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    process = models.BooleanField()

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.sensor)
    
@auto_admin_register()
class safetyAlert(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    safetyId = models.ForeignKey(Safety, on_delete=models.CASCADE, related_name='safety_alert_id', null=False)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name