from django.db import models
import django.utils.timezone as timezone


# Create your models here.

class Point(models.Model):
    '''Risk Point table'''

    place = models.CharField(max_length=16, verbose_name="place", blank=True, null=True)
    longitude = models.CharField(max_length=32, verbose_name="lon")
    latitude = models.CharField(max_length=32, verbose_name="lan")
    time = models.DateField(verbose_name="updatetime", auto_now_add=True)
    Infected = models.CharField(max_length=32, verbose_name="infected", blank=True, null=True)

    class Meta:
        verbose_name = 'riskPoint'
        verbose_name_plural = verbose_name

class Risk(models.Model):
    '''Risk table'''

    place = models.CharField(max_length=16, verbose_name="place", blank=True, null=True)
    longitude = models.CharField(max_length=32, verbose_name="lon")
    latitude = models.CharField(max_length=32, verbose_name="lan")
    time = models.DateField(verbose_name="updatetime", auto_now_add=True)
    Infected = models.CharField(max_length=32, verbose_name="infected", blank=True, null=True)

    class Meta:
        verbose_name = 'risk'
        verbose_name_plural = verbose_name
