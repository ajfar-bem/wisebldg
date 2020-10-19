from django.db import models
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import JSONField


import uuid
import os

class BemossAccount(models.Model): #all bemoss accounts, go here. Admins, Owners, zone managers, tennats all belong to a unique account.
    account_id = models.TextField(primary_key=True,blank=False) #can use contract ID
    account_name = models.TextField(blank=False)
    description = models.TextField()
    device_limit = models.IntegerField() #Allowed Number of approved devices
    device_type_allowed = models.ManyToManyField('deviceinfos.DeviceType') #list of allowed device types
    applications_allowed = models.ManyToManyField('bemoss_applications.ApplicationRegistered') #list allowed application types
    class Meta:
        db_table = "bemoss_account"

class BemossToken(models.Model): # Stores temporary tokens created to allow new users to register under a account (admins, zone-mangers etc) to create their login credentials.
    token = models.UUIDField(primary_key=True) #the unique token
    account = models.ForeignKey(BemossAccount) #the account to which the new user (who will be using the token) belongs to
    email = models.EmailField() #the email address
    auth_user_group = models.ForeignKey(Group)# the (privilege group this user should belong to)
    building = models.ForeignKey('buildinginfos.BuildingInfo', null=True) #the building this user is allowed to use. Null value gives access to all buildings under the account
    expiration_date = models.DateTimeField() #the token can't be used to create user past this date
    zone = models.ForeignKey('buildinginfos.ZoneInfo', null=True) # null value gives access to all zones under the building.
    class Meta:
        db_table = "bemoss_token"



