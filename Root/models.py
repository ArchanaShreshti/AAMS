from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField 
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib import admin
from functools import wraps
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from django_mongodb_backend.fields import ObjectIdAutoField 
from django.core.exceptions import ValidationError
import json
from bson import ObjectId

class HistoricalModel(models.Model):
    history = HistoricalRecords()

    class Meta:
        abstract = True

def auto_admin_register(model_admin=None):
    def decorator(model):
        if model_admin:
            admin.site.register(model, model_admin)
        else:
            admin.site.register(model)
        return model
    return decorator

@auto_admin_register()
class Area(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    customerId=models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='customer_id', blank=False, null=False)
    description= models.TextField()
    parentId=models.ForeignKey('self', on_delete=models.CASCADE, related_name='customer_parentId', blank=True, null=True)
    
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

@auto_admin_register()
class Customer(models.Model):
    id = ObjectIdAutoField(primary_key=True)  # This is equivalent to ObjectId for MongoDB (auto-incremented)
    name = models.CharField(max_length=255, null=False)
    logo = models.URLField(max_length=500, blank=True, null=True)  # URL for logo
    siteImage = models.URLField(max_length=500, blank=True, null=True)  # URL for site image
    latitude = models.CharField(max_length=100)  # Latitude as a string (may consider using FloatField)
    longitude = models.CharField(max_length=100)  # Longitude as a string (may consider using FloatField)
    areas = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='customer_areas', blank=True, null=True)  # Linking to Area
    subareas = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='customer_subareas', blank=True, null=True)  # Linking to SubArea
    
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

@auto_admin_register()
class Alert(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    assetId = models.ForeignKey('Machine', on_delete=models.CASCADE, related_name='root_alert', blank=False, null=False)
    sensorId = models.ForeignKey('Vibration.Sensor', on_delete=models.CASCADE, related_name='root_alert', blank=False, null=False)
    statusId = models.ForeignKey('Status', on_delete=models.CASCADE, related_name='root_alert', blank=False, null=False)
    date = models.DateTimeField(default=datetime.now)
    description = models.TextField()
    
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.description
    
@auto_admin_register()
class User(AbstractUser):
    id = ObjectIdAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    customerId = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=255,  null=False, blank=False)
    theme = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    notification = models.JSONField(null=True)
    token = models.CharField(max_length=1024, null=True)
    isSuperAdmin = models.BooleanField(default=False)
    licenseKey = models.CharField(max_length=255, null=True)
    licenseAdded = models.BooleanField(default=False)
    applicationLicenseKey = models.CharField(max_length=255, null=True)
    applicationLicenseAdded = models.BooleanField(default=False)
    
    # Many-to-many relationships for groups and permissions
    groups = models.ManyToManyField(settings.AUTH_GROUP_MODEL, related_name='user_groups', blank=True)
    userPermissions = models.ManyToManyField(settings.AUTH_PERMISSION_MODEL, related_name='user_permissions', blank=True)
    
    role = models.CharField(
        max_length=20, choices=[
            ('Admin', 'Admin'),
            ('Manager', 'Manager'),
            ('Employee', 'Employee'),
            ('customer', 'Customer'),
            ('customerAdmin', 'CustomerAdmin'),
            ('Analyst', 'Analyst'),
        ]
    )
    
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    class Meta:
        swappable = 'AUTH_USER_MODEL'
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        if self._password:
            self.set_password(self._password)
        super().save(*args, **kwargs)

class Permission(Permission):
    PermissionId = ObjectIdAutoField(primary_key=True)
    Permissionname = models.CharField(max_length=255)
    contentType = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='custom_permission_content_type')
    codeName = models.CharField(max_length=255)

    class Meta:
            swappable = 'AUTH_PERMISSION_MODEL'

class Group(Group):
    GroupId = ObjectIdAutoField(primary_key=True)
    Groupname = models.CharField(max_length=150, unique=True)
    Permissions = models.ManyToManyField(Permission, related_name='custom_group_permissions', blank=True)

    class Meta:
        swappable = 'AUTH_GROUP_MODEL'

Group._meta.get_field('id').__class__ = ObjectIdAutoField
Permission._meta.get_field('id').__class__ = ObjectIdAutoField
LogEntry._meta.get_field('id').__class__ = ObjectIdAutoField

@auto_admin_register()
class Status(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=True)
    key = models.CharField(max_length=255, unique=True, null=False)
    color = models.CharField(max_length=255, blank=True)
    badgeClass = models.CharField(max_length=255, blank=True)
    severity = models.IntegerField()

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Location validation
def validateLocation(value):
    # If value is a string, try to parse it as JSON
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            raise ValidationError('Invalid JSON string')
    
    # Check if value is a dictionary
    if not isinstance(value, dict):
        raise ValidationError('Location must be a dictionary or valid JSON string')
    
    # Validate the location type (should be "Point")
    if value.get('type') != 'Point':
        raise ValidationError('Invalid location type')
    
    # Validate the coordinates field (should be a list of 2 numbers)
    coordinates = value.get('coordinates', [])
    if not isinstance(coordinates, list) or len(coordinates) != 2:
        raise ValidationError('Invalid coordinates - must be an array of 2 numbers [longitude, latitude]')

# Default email function
def default_email():
    return ['akshay@enmaz.com', 'jayanth@enmaz.com', 'gnraju@aswartha.com']

@auto_admin_register()
class Machine(models.Model):
    id = ObjectIdAutoField(primary_key=True)  # Use ObjectIdAutoField for primary key
    name = models.CharField(max_length=255, blank=False, null=False)
    tagNumber = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    powerRating = models.CharField(max_length=255, blank=True, null=True)
    observations = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    machineType = models.CharField(max_length=255, blank=True, null=True)
    location = models.JSONField(validators=[validateLocation])
    technologyId = models.ForeignKey('Root.Technology', on_delete=models.CASCADE)
    statusId = models.ForeignKey('Root.Status', on_delete=models.CASCADE, default='65642670e8b6d946f53bf31c')
    customerId = models.ForeignKey('Root.Customer', on_delete=models.CASCADE, blank=False, null=False)
    areaId = models.ForeignKey('Root.Area', on_delete=models.CASCADE, related_name='machine_area', blank=False, null=False)
    subAreaId = models.ForeignKey('Root.Area', on_delete=models.CASCADE, related_name='machine_sub_area', blank=False, null=False)
    alertLimitsId = models.ForeignKey('Root.AlertLimits', on_delete=models.CASCADE, blank=True, null=True)
    rpm = models.IntegerField(blank=False, null=False)
    preventiveCheckList = models.JSONField(blank=True, null=True)
    preventiveCheckData = models.JSONField(blank=True, null=True)
    messageSendTime = models.DateTimeField(blank=True, null=True)
    contactNumber = models.JSONField(blank=True, null=True)
    qrCode = models.URLField(blank=True, null=True)
    dataUpdatedTime = models.DateTimeField(auto_now=True)
    email = models.JSONField(default=default_email)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Machine'
        verbose_name_plural = 'Machines'

    def save(self, *args, **kwargs):
    # Ensure location is a valid JSON format (if it's a dictionary)
        if isinstance(self.location, dict):
            self.location = json.dumps(self.location)

        # Validate required fields
        required_fields = ['name', 'tagNumber', 'location', 'customerId', 'areaId', 'subAreaId', 'rpm']
        missing_fields = [field for field in required_fields if not getattr(self, field)]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

        # Save the object
        super().save(*args, **kwargs)
    
@auto_admin_register()
class Bearing(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    bearingNumber = models.CharField(max_length=255, null=False)
    type = models.CharField(max_length=255, null=False)
    innerRacePass = models.FloatField(null=False)
    outerRacePass = models.FloatField(null=False)
    rollElementPass = models.FloatField(null=False)
    cageRotation = models.FloatField(null=False)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ObjectIdEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

@auto_admin_register()
class BearingLocation(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    machineId = models.ForeignKey('Machine', on_delete=models.CASCADE)
    bearingId = models.ForeignKey('Bearing', on_delete=models.CASCADE)
    bearingLocationType = models.CharField(max_length=255)

    velocity = models.JSONField()
    acceleration = models.JSONField()
    accelerationEnvelope = models.JSONField()
    orientation = models.JSONField()

    dataFetchingInterval = models.IntegerField()
    rawDataSavingInterval = models.DateTimeField(null=True, blank=True)
    statusId = models.ForeignKey('Status', on_delete=models.CASCADE, default='65642670e8b6d946f53bf31c')
    dataStoreFlag = models.BooleanField(default=False)
    averagingFlag = models.IntegerField(default=0)
    fSpanMin = models.IntegerField(default=8)
    fSpanMax = models.IntegerField(default=800)
    lowFrequencyFmax = models.FloatField(null=True, blank=True)
    lowFrequencyNoOflines = models.IntegerField(null=True, blank=True)
    mediumFrequencyFmax = models.FloatField(null=True, blank=True)
    mediumFrequencyNoOflines = models.IntegerField(null=True, blank=True)
    highFrequencyFmax = models.FloatField(null=True, blank=True)
    highFrequencyNoOflines = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_values = {
            'velocity': {
                'highpassCutoffFrequency': 10,
                'highpassOrder': 4,
                'highpassCutoffFrequencyFft': 10,
                'highpassOrderFft': 4,
                'calibrationValue': {
                    'h': 1,
                    'v': 1,
                    'a': 1
                },
                'highpassFilterRequired': False,
                'lowpassCutoffFrequency': 5000,
                'lowpassOrder': 2,
                'floorNoiseThresholdPercentage': {
                    'h': 5,
                    'v': 5,
                    'a': 5
                },
                'floorNoiseAttenuationFactor': {
                    'h': 4,
                    'v': 4,
                    'a': 4
                }
            },
            'acceleration': {
                'highpassCutoffFrequency': 10,
                'highpassOrder': 4,
                'highpassCutoffFrequencyFft': 10,
                'highpassOrderFft': 4,
                'calibrationValue': {
                    'h': 1,
                    'v': 1,
                    'a': 1
                },
                'highpassFilterRequired': False,
                'lowpassCutoffFrequency': 5000,
                'lowpassOrder': 2,
                'floorNoiseThresholdPercentage': {
                    'h': 5,
                    'v': 5,
                    'a': 5
                },
                'floorNoiseAttenuationFacter': {
                    'h': 4,
                    'v': 4,
                    'a': 4
                }
            },
            'accelerationEnvelope': {
                'highpassCutoffFrequency': 10,
                'highpassOrder': 4,
                'highpassCutoffFrequencyFft': 10,
                'highpassOrderFft': 4,
                'calibrationValue': {
                    'h': 1,
                    'v': 1,
                    'a': 1
                },
                'highpassFilterRequired': False,
                'lowpassCutoffFrequency': 5000,
                'lowpassOrder': 2,
                'floorNoiseThresholdPercentage': {
                    'h': 5,
                    'v': 5,
                    'a': 5
                },
                'floorNoiseAttenuationFacter': {
                    'h': 4,
                    'v': 4,
                    'a': 4
                }
            },
            'orientation': {
                'h': {
                    'channel': '',
                    'sensorId': ''
                },
                'v': {
                    'channel': '',
                    'sensorId': ''
                },
                'a': {
                    'channel': '',
                    'sensorId': ''
                },
                'x': '',
                'y': '',
                'z': ''
            }
        }
        
    def save(self, *args, **kwargs):
        for field, default_value in self.default_values.items():
            current_value = getattr(self, field)
            if not current_value:
                setattr(self, field, default_value)
        super().save(*args, **kwargs)

    """ def to_dict(self):
        data = {}
        for field in self._meta.get_fields():
            value = getattr(self, field.name)
            if isinstance(value, ObjectId):
                data[field.name] = str(value)
            elif field.many_to_many:
                data[field.name] = [str(obj.id) for obj in value.all()]
            elif field.many_to_one or field.one_to_one:
                if field.name in ['machineId', 'bearingId', 'statusId']:
                    data[field.name] = str(value.id)
                else:
                    data[field.name] = value
            else:
                if isinstance(value, dict):
                    data[field.name] = value.copy()  # Make a copy to avoid modifying the original data
                    for k, v in data[field.name].items():
                        if isinstance(v, ObjectId):
                            data[field.name][k] = str(v)
                        elif isinstance(v, dict):
                            data[field.name][k] = {kk: str(vv) if isinstance(vv, ObjectId) else vv for kk, vv in v.items()}
                else:
                    data[field.name] = value
        return data

    def to_json(self):
        return json.dumps(self.to_dict(), cls=ObjectIdEncoder) """

@auto_admin_register()
class Technology(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    key = models.CharField(max_length=255, unique=True, null=False)
    description = models.TextField(blank=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
@auto_admin_register()
class TechnologyParameter(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    key = models.CharField(max_length=255, unique=True, null=False)
    description = models.TextField(blank=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
@auto_admin_register()
class Orientation(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    key = models.CharField(max_length=255, blank=False, null=False, unique=True)
    description = models.TextField(blank=True, null=True)
    customerId = models.ForeignKey('Customer', on_delete=models.CASCADE, blank=False, null=False)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Orientation'
        verbose_name_plural = 'Orientations'

@auto_admin_register()
class Foundation(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    key = models.CharField(max_length=255, blank=False, null=False, unique=True)
    description = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Foundation'
        verbose_name_plural = 'Foundations'

@auto_admin_register()
class AlertLimits(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    type = models.IntegerField()  # Corresponding to the 'type' field
    normal = models.FloatField()
    satisfactory = models.FloatField()
    alert = models.FloatField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Alert Limit'
        verbose_name_plural = 'Alert Limits'

    class Meta:
        verbose_name = 'Alert Limits'
        verbose_name_plural = 'Alert Limits'

User = get_user_model()

class UserActivityLog(models.Model):
    id = ObjectIdAutoField(primary_key=True, unique=True)
    ACTION_CHOICES = (
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    modelName = models.CharField(max_length=255, null=True, blank=True)
    objectId = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} - {self.timestamp}"