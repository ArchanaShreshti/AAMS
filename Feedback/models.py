from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField 
from Root.models import auto_admin_register

@auto_admin_register()
class Feedback(models.Model):
    id=ObjectIdAutoField(primary_key=True)
    feedbackDescription = models.TextField()
    priority=models.IntegerField()
    parentFeedbackId = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.feedbackResponse

@auto_admin_register
class FeedbackAlert(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    feedbackId = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='feedback_alert_id')
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name