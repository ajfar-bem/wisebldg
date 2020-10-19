from __future__ import unicode_literals

from django.db import models
from webapps.buildinginfos.models import BuildingInfo

class oauthToken(models.Model):

    class Meta:
        db_table = 'oauth_token'

    token_id = models.AutoField(primary_key=True)
    service_provider = models.CharField(max_length=100)
    token = models.CharField(max_length=1000)
    obtained_time = models.DateTimeField()
    building = models.ForeignKey(BuildingInfo, null=False)  # cannot be null
