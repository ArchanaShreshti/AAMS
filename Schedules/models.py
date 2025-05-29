from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField
from Root.models import auto_admin_register, Machine

@auto_admin_register()
class Schedule(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    customerId = models.ForeignKey('Root.Customer', on_delete=models.CASCADE, null=False)
    startDate = models.DateTimeField(null=False)
    endDate = models.DateTimeField(null=False)
    frequency = models.IntegerField(null=False)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.customer)
    
@auto_admin_register()
class ScheduleTask(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    customerId = models.ForeignKey('Root.Customer', on_delete=models.CASCADE, null=False)
    machineId = models.ForeignKey('Root.Machine', on_delete=models.CASCADE, null=False)
    userId = models.ForeignKey('Root.User', on_delete=models.CASCADE, null=False)
    scheduleId = models.ForeignKey('Schedule', on_delete=models.CASCADE, null=True, blank=True)
    technologyId = models.ForeignKey('Root.Technology', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(null=False)
    severityId = models.ForeignKey('Root.Status', on_delete=models.CASCADE)
    observation = models.TextField(blank=True)
    priority = models.CharField(max_length=255, blank=True)
    recommendation = models.TextField(blank=True)
    approvalStatus = models.CharField(max_length=255, blank=True)
    reportType = models.CharField(max_length=255, blank=True)
    report = models.TextField(blank=True)
    image = models.CharField(max_length=255, blank=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.machine)
    
@auto_admin_register()
class DailyTaskSchedule(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    customerId = models.ForeignKey('Root.Customer', on_delete=models.CASCADE, db_index=True, blank=False, null=False)
    machineId = models.JSONField(blank=False, null=False)  # List of machine IDs
    date = models.DateField(blank=False, null=False)
    userId = models.ForeignKey('Root.User', on_delete=models.CASCADE, db_index=True, blank=False, null=False)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Daily Task Schedule'
        verbose_name_plural = 'Daily Task Schedules'

    def save(self, *args, **kwargs):
        required_fields = ['customerId', 'machineId', 'date', 'userId']
        missing_fields = []
        for field in required_fields:
            if field not in self.__dict__:
                missing_fields.append(field)

        if 'machineId' in self.__dict__:
            if not isinstance(self.machineId, list):
                missing_fields.append('machineId must be a list')
            else:
                for machine in self.machineId:
                    try:
                        Machine.objects.get(id=machine)
                    except Machine.DoesNotExist:
                        missing_fields.append(f'Machine ID {machine} does not exist')

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        super().save(*args, **kwargs)
    
@auto_admin_register
class scheduleAlert(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    scheduleId = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='schedule_alert_id', null=False)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    