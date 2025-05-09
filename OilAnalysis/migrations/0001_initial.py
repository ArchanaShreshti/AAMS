# Generated by Django 5.1.8 on 2025-05-05 07:28

import django.utils.timezone
import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OilAnalysis',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(primary_key=True, serialize=False)),
                ('rubbingWear', models.BooleanField(default=False)),
                ('slidingWear', models.BooleanField(default=False)),
                ('cuttingWear', models.BooleanField(default=False)),
                ('gearWear', models.BooleanField(default=False)),
                ('bearingWear', models.BooleanField(default=False)),
                ('spheres', models.BooleanField(default=False)),
                ('darkMetalloOxide', models.BooleanField(default=False)),
                ('redOxides', models.BooleanField(default=False)),
                ('corrosiveWearDebris', models.BooleanField(default=False)),
                ('whiteNonferrousParticles', models.BooleanField(default=False)),
                ('copper', models.BooleanField(default=False)),
                ('others', models.CharField(max_length=50)),
                ('othersOptional', models.CharField(blank=True, max_length=50, null=True)),
                ('frictionsPolymers', models.BooleanField(default=False)),
                ('sandDirt', models.BooleanField(default=False)),
                ('fibers', models.BooleanField(default=False)),
                ('othersContaminant', models.CharField(blank=True, max_length=50, null=True)),
                ('kinematicViscosity40c', models.FloatField()),
                ('kinematicViscosity100c', models.FloatField()),
                ('viscosityIndex', models.FloatField()),
                ('moistureContent', models.FloatField()),
                ('tan', models.FloatField()),
                ('flashPoint', models.FloatField(blank=True, null=True)),
                ('tbn', models.FloatField(blank=True, null=True)),
                ('density', models.FloatField(blank=True, null=True)),
                ('conePenetration', models.FloatField(blank=True, null=True)),
                ('dropPoint', models.FloatField(blank=True, null=True)),
                ('particleCountNAS', models.IntegerField()),
                ('particleCountISO', models.IntegerField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='oilAnalysisAlert',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
