from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField
from Root.models import auto_admin_register
from django.utils import timezone
from Root.models import AlertLimits

@auto_admin_register
class OilAnalysis(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    machineID = models.ForeignKey('Root.Machine', on_delete=models.CASCADE, null=False)
    rubbingWear = models.BooleanField(default=False)
    slidingWear = models.BooleanField(default=False)
    cuttingWear = models.BooleanField(default=False)
    gearWear = models.BooleanField(default=False)
    bearingWear = models.BooleanField(default=False)
    spheres = models.BooleanField(default=False)
    darkMetalloOxide = models.BooleanField(default=False)
    redOxides = models.BooleanField(default=False)
    corrosiveWearDebris = models.BooleanField(default=False)
    whiteNonferrousParticles = models.BooleanField(default=False)
    copper = models.BooleanField(default=False)
    others = models.CharField(max_length=50, blank=False, null=False)
    othersOptional = models.CharField(max_length=50, blank=True, null=True)
    frictionsPolymers = models.BooleanField(default=False)
    sandDirt = models.BooleanField(default=False)
    fibers = models.BooleanField(default=False)
    othersContaminant = models.CharField(max_length=50, blank=True, null=True)
    kinematicViscosity40c = models.FloatField(blank=False, null=False)
    kinematicViscosity100c = models.FloatField(blank=False, null=False)
    viscosityIndex = models.FloatField(blank=False, null=False)
    moistureContent = models.FloatField(blank=False, null=False)
    tan = models.FloatField(blank=False, null=False)
    flashPoint = models.FloatField(blank=True, null=True)
    tbn = models.FloatField(blank=True, null=True)
    density = models.FloatField(blank=True, null=True)
    conePenetration = models.FloatField(blank=True, null=True)
    dropPoint = models.FloatField(blank=True, null=True)
    particleCountNAS = models.IntegerField(blank=False, null=False)
    particleCountISO = models.IntegerField(blank=False, null=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"OilAnalysis('{self.id}')"
    
@auto_admin_register
class oilAnalysisAlert(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    AssetId = models.ForeignKey('Root.Machine', on_delete=models.CASCADE, related_name='oil_analysis_alert_id')
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
