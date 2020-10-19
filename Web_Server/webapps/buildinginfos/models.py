# -*- coding: utf-8 -*-
from django.core.validators import MinValueValidator, MaxValueValidator
from webapps.bemoss_accounts.models import BemossAccount
from django.contrib.postgres.fields import JSONField

from django.db import models
import uuid
import os

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('uploads/buildingmap/', filename)

class BuildingMap(models.Model):


    bmap_file_location = models.ImageField(upload_to=get_file_path)

    class Meta:
        db_table = 'building_map'

    def __str__(self):
        return self.bmap_file_location

    def __unicode__(self):
        return self.id

class BuildingInfo(models.Model):
    building_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=False)
    account = models.ForeignKey(BemossAccount)
    zip_code = models.TextField(blank=True)
    description = models.TextField(blank=True)
    building_settings = JSONField(default={})
    class Meta:
        db_table = 'building_info'


class ZoneInfo(models.Model):
    zone_id = models.AutoField(primary_key=True)
    zone_nickname = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    building = models.ForeignKey(BuildingInfo)
    zone_settings = JSONField(default={})

    class Meta:
        db_table = "building_zone"


    def __unicode__(self):
        return str(self.zone_id)

    def as_json(self):
        return dict(
            id=self.zone_id,
            zone_nickname=self.zone_nickname.encode('utf-8').title())

    def data_dashboard_global(self):
        gsetting = GlobalSetting.objects.get(zone=self)
        global_setting = GlobalSetting.as_json(gsetting)
        return dict(
            id=self.zone_id,
            zone_nickname=self.zone_nickname.encode('utf-8').title() if self.zone_nickname else '',
            global_setting=global_setting,
        )

    def data_dashboard(self):
        gsetting = GlobalSetting.objects.get(zone=self)
        global_setting = GlobalSetting.as_json(gsetting)
        return dict(
            id=self.zone_id,
            zone_nickname=self.zone_nickname.encode('utf-8').title() if self.zone_nickname else '',
            global_setting=global_setting,
            t_count=0,
            pl_count=0,
            lt_count=0,
            ss_count=0,
            pm_count=0
        )


class GlobalSetting(models.Model):
    zone = models.ForeignKey(ZoneInfo)
    heat_setpoint = models.IntegerField(null=True, blank=True)
    cool_setpoint = models.IntegerField(null=True, blank=True)
    illuminance = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True,
                                              blank=True)

    class Meta:
        db_table = "global_zone_setting"

    def __unicode__(self):
        return self.id

    def as_json(self):
        return dict(
            zone=self.zone,
            heat_setpoint=self.heat_setpoint,
            cool_setpoint=self.cool_setpoint,
            illumination=self.illuminance
        )



class IOTGateway(models.Model):
    gateway = models.IntegerField(primary_key=True,auto_created=True)
    account = models.ForeignKey(BemossAccount)
    building = models.ForeignKey(BuildingInfo)
    gateway_name = models.TextField()
    date_attached = models.DateTimeField()
    status=models.TextField(null=True, blank=True)
    gateway_settings = JSONField(default={})
    class Meta:
        db_table = 'iot_gateway'