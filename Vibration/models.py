from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField
from Root.models import auto_admin_register
from django.core.exceptions import ValidationError
from Root.models import AlertLimits

@auto_admin_register()
class Sensor(models.Model):
    id = ObjectIdAutoField(primary_key=True)  # MongoDB ObjectId as the primary key
    customerId = models.ForeignKey('Root.Customer', on_delete=models.CASCADE, db_index=True)
    machineId = models.ForeignKey('Root.Machine', on_delete=models.CASCADE, db_index=True)
    bearingLocationId = models.ForeignKey('Root.BearingLocation', on_delete=models.CASCADE, db_index=True)
    technologyParameterId = models.ForeignKey('Root.TechnologyParameter', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    serialNumber = models.CharField(max_length=255, blank=True, null=True)
    statusId = models.ForeignKey('Root.Status', on_delete=models.CASCADE, null=True, blank=True)
    gRange = models.FloatField(blank=True, null=True)
    ssid = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    value = models.JSONField(null=True, blank=True)  # Store any object in JSON format (similar to Mongoose's Object)
    configuration = models.BooleanField(blank=True, null=True)
    reportingFrequency = models.IntegerField(null=True, blank=True)
    samplingFrequency = models.IntegerField(null=True, blank=True)
    numberOfSamples = models.IntegerField(null=True, blank=True)
    postUrl = models.URLField(default="https://dl6a9qlj1b.execute-api.ap-southeast-1.amazonaws.com/PROD/online/dataPush")
    tFlag = models.BooleanField(default=False)
    
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensors'

    def clean(self):
        if not self.name:
            raise ValidationError({'name': 'Name is required.'})

    def save(self, *args, **kwargs):
        required_fields = ['name']
        missing_fields = [field for field in required_fields if not getattr(self, field, None)]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        super().save(*args, **kwargs)

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        super().save(*args, **kwargs)
    
@auto_admin_register()
class ParameterTrend(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    bearingLocationId = models.ForeignKey('Root.BearingLocation', on_delete=models.CASCADE)
    epochTime = models.CharField(max_length=255, blank=False, null=False)
    data = models.JSONField(blank=False, null=False)
    rawDataPresent = models.BooleanField(blank=False, null=False)
    axis = models.CharField(max_length=255, blank=False, null=False)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Parameter Trend'
        verbose_name_plural = 'Parameter Trends'

    def save(self, *args, **kwargs):
        required_fields = ['epochTime', 'data', 'rawDataPresent', 'axis']
        missing_fields = []
        for field in required_fields:
            if field not in self.__dict__:
                missing_fields.append(field)

        data_required_fields = ['H', 'V', 'A']
        for field in data_required_fields:
            if field not in self.data:
                missing_fields.append(f"Data.{field}")

        for field in data_required_fields:
            axis_required_fields = ['velocity', 'acceleration', 'accelerationEnvelope']
            for axis_field in axis_required_fields:
                if axis_field not in self.data[field]:
                    missing_fields.append(f"Data.{field}.{axis_field}")

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        super().save(*args, **kwargs)
    
@auto_admin_register()
class RawData(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    bearingLocationId = models.ForeignKey('Root.BearingLocation', on_delete=models.CASCADE)
    epochTime = models.CharField(max_length=255, blank=False, null=False)
    data = models.JSONField(blank=False, null=False)
    axis = models.CharField(max_length=255, blank=False, null=False)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Raw Data'
        verbose_name_plural = 'Raw Data'

    def save(self, *args, **kwargs):
        required_fields = ['epochTime', 'data', 'axis']
        missing_fields = []
        for field in required_fields:
            if field not in self.__dict__:
                missing_fields.append(field)

        data_required_fields = ['H', 'V', 'A']
        for field in data_required_fields:
            if field not in self.data:
                missing_fields.append(f"Data.{field}")

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        super().save(*args, **kwargs)

@auto_admin_register
class LatestData(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    bearingLocationId = models.ForeignKey('Root.BearingLocation', on_delete=models.CASCADE)
    epochTime = models.CharField(max_length=255, blank=False, null=False)
    data = models.JSONField(blank=False, null=False)
    axis = models.CharField(max_length=255, blank=False, null=False)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Latest Data'
        verbose_name_plural = 'Latest Data'

    def save(self, *args, **kwargs):
        required_fields = ['epochTime', 'data', 'axis']
        missing_fields = []
        for field in required_fields:
            if field not in self.__dict__:
                missing_fields.append(field)

        data_required_fields = ['H', 'V', 'A']
        for field in data_required_fields:
            if field not in self.data:
                missing_fields.append(f"Data.{field}")

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        super().save(*args, **kwargs)

@auto_admin_register
class LatestRMSData(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    bearingLocationId = models.ForeignKey('Root.BearingLocation', on_delete=models.CASCADE)
    epochTime = models.CharField(max_length=255, blank=False, null=False)
    data = models.JSONField(blank=False, null=False)
    axis = models.CharField(max_length=255, blank=False, null=False)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Latest RMS Data'
        verbose_name_plural = 'Latest RMS Data'

    def save(self, *args, **kwargs):
        required_fields = ['epochTime', 'data', 'axis']
        missing_fields = []
        for field in required_fields:
            if field not in self.__dict__:
                missing_fields.append(field)

        data_required_fields = ['H', 'V', 'A']
        for field in data_required_fields:
            if field not in self.data:
                missing_fields.append(f"Data.{field}")

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        super().save(*args, **kwargs)

@auto_admin_register()
class MultiChannelSensor(models.Model):
    id=ObjectIdAutoField(primary_key=True)
    customerId = models.ForeignKey('Root.Customer', on_delete=models.CASCADE)
    machineId = models.ForeignKey('Root.Machine', on_delete=models.CASCADE)
    bearingLocationId = models.JSONField(default=list)
    technologyParameterId = models.ForeignKey('Root.Technology', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=False, null=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    serialNumber = models.CharField(max_length=255, blank=True, null=True)
    statusId = models.ForeignKey('Root.Status', on_delete=models.CASCADE)
    gRange = models.FloatField(blank=True, null=True)
    ssid = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    value = models.JSONField(blank=True, null=True)
    configuration = models.BooleanField(blank=True, null=True)
    reportingFrequency = models.FloatField(blank=True, null=True)
    samplingFrequency = models.FloatField(blank=True, null=True)
    numberOfSamples = models.FloatField(blank=True, null=True)
    threshold = models.FloatField(blank=True, null=True)
    csf = models.FloatField(blank=True, null=True)
    postUrl = models.CharField(max_length=255, default="https://dl6a9qlj1b.execute-api.ap-southeast-1.amazonaws.com/PROD/AAMS/MULTI_CHANNEL")

    def clean(self):
        if not self.address and not self.serialNumber:
            raise ValidationError('At least one of address or serialNumber must be present.')
        if self.serialNumber:
            self.postUrl = "https://dl6a9qlj1b.execute-api.ap-southeast-1.amazonaws.com/PROD/AAMS/MULTI_CHANNEL"
        else:
            self.postUrl = "https://dl6a9qlj1b.execute-api.ap-southeast-1.amazonaws.com/PROD/online/dataPush"

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Multi Channel Sensor'
        verbose_name_plural = 'Multi Channel Sensors'

@auto_admin_register()
class vibrationAlert(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    AssetId = models.ForeignKey('Root.Machine', on_delete=models.CASCADE, related_name='Vib_alert_id', null=False)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

@auto_admin_register
class AlertLimits(AlertLimits):
    class Meta:
        proxy = True