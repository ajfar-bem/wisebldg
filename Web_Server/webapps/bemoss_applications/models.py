from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField
from webapps.bemoss_accounts.models import BemossAccount
from webapps.buildinginfos.models import BuildingInfo,ZoneInfo


class ApplicationRegistered(models.Model):

    class Meta:
        db_table = 'application_registered'

    application_id = models.AutoField(primary_key=True)
    app_name = models.CharField(max_length=50,blank=True,null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    app_agent = models.CharField(max_length=200, blank=False, null=False)
    registered_time = models.DateTimeField()

    def __unicode__(self):
        return str(self.as_json())

    def as_json(self):
        return dict(
            application_id = self.application_id,
            app_name = self.app_name.encode().encode('utf-8').title(),
            description = self.description.encode().encode('utf-8').title(),
            app_agent = self.app_agent.encode().encode('utf-8').title(),
            registered_time = self.registered_time)


class ApplicationRunning(models.Model):

    class Meta:
        db_table = 'application_running'

    #id = models.IntegerField(primary_key=True,auto_created=True)
    start_time = models.DateTimeField()
    app_agent_id = models.CharField(max_length=50,null=False)
    status = models.CharField(max_length=20,blank=True,null=True)
    app_type = models.ForeignKey(ApplicationRegistered)
    app_data = JSONField(default={})
    building = models.ForeignKey(BuildingInfo,null=True) # if null, this apps belong to all building
    zone = models.ForeignKey(ZoneInfo, null=True) # if null, app belongs to all zone
