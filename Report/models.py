from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField
from Root.models import auto_admin_register

@auto_admin_register()
class MachineReport(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    machine = models.ForeignKey('Root.Machine', on_delete=models.CASCADE, null=False)
    sensor = models.ForeignKey('Vibration.Sensor', on_delete=models.CASCADE, null=False)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.machine)
    
@auto_admin_register()
class ImageReport(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    machineReportId = models.ForeignKey('MachineReport', on_delete=models.CASCADE, db_index=True)
    plotType = models.CharField(max_length=255, blank=False, null=False)
    imageURL = models.URLField(blank=False, null=False)
    imageDescription = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Image Report'
        verbose_name_plural = 'Image Reports'

    def save(self, *args, **kwargs):
        required_fields = ['plotType', 'imageURL']
        missing_fields = []
        for field in required_fields:
            if field not in self.__dict__:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        super().save(*args, **kwargs)

@auto_admin_register()
class OilAnalysisReport(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    equipmentId = models.ForeignKey('OilAnalysis.OilAnalysis', on_delete=models.CASCADE, db_index=True, blank=False, null=False)
    recievedDate = models.DateField(blank=True, null=True)
    reportDate = models.DateField(blank=True, null=True)
    condition = models.ForeignKey('Root.Status', on_delete=models.CASCADE, blank=True, null=True)
    sampleId = models.CharField(max_length=255, blank=False, null=False)
    oaKinematicViscosity40C = models.CharField(max_length=255, blank=True, null=True)
    OaMoistureContent = models.CharField(max_length=255, blank=True, null=True)
    OaKinematicViscosity100C = models.CharField(max_length=255, blank=True, null=True)
    OaTotalAcidNumber = models.CharField(max_length=255, blank=True, null=True)
    OaRecommendations = models.TextField(blank=True, null=True)
    OaAbnormalities = models.TextField(blank=True, null=True)
    fwRubbingWear = models.CharField(max_length=255, blank=True, null=True)
    fwSlidingWear = models.CharField(max_length=255, blank=True, null=True)
    fwCuttingWear = models.CharField(max_length=255, blank=True, null=True)
    fwChunks = models.CharField(max_length=255, blank=True, null=True)
    fwReworked = models.CharField(max_length=255, blank=True, null=True)
    fwSpheres = models.CharField(max_length=255, blank=True, null=True)
    fwDarkMetalloOxides = models.CharField(max_length=255, blank=True, null=True)
    fwRedOxides = models.CharField(max_length=255, blank=True, null=True)
    fwCorrosiveWearDebris = models.CharField(max_length=255, blank=True, null=True)
    fwOtherParameters = models.CharField(max_length=255, blank=True, null=True)
    fwValue = models.CharField(max_length=255, blank=True, null=True)
    fwFerrousDebrisCount = models.CharField(max_length=255, blank=True, null=True)
    nfwRubbingWear = models.CharField(max_length=255, blank=True, null=True)
    nfwSlidingWear = models.CharField(max_length=255, blank=True, null=True)
    nfwCuttingWear = models.CharField(max_length=255, blank=True, null=True)
    nfwGearWear = models.CharField(max_length=255, blank=True, null=True)
    nfwBearingWear = models.CharField(max_length=255, blank=True, null=True)
    nfwWhiteNonFerrousParticles = models.CharField(max_length=255, blank=True, null=True)
    coFrictionPolymers = models.CharField(max_length=255, blank=True, null=True)
    coNonMetallicCrystalline = models.CharField(max_length=255, blank=True, null=True)
    coFibers = models.CharField(max_length=255, blank=True, null=True)
    coOther = models.CharField(max_length=255, blank=True, null=True)
    coWearParticlesImage = models.CharField(max_length=255, blank=True, null=True)
    coImageTitle = models.CharField(max_length=255, blank=True, null=True)
    abnormalities = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    resultDiscussion = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Oil Analysis Report'
        verbose_name_plural = 'Oil Analysis Reports'

    def save(self, *args, **kwargs):
        required_fields = ['equipmentId', 'sampleId']
        missing_fields = []
        for field in required_fields:
            if field not in self.__dict__:
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        super().save(*args, **kwargs)
