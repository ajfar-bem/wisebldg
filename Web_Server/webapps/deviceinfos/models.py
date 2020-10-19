from django.db import models

from webapps.multinode.models import NodeInfo
from webapps.buildinginfos.models import BuildingInfo,ZoneInfo, IOTGateway
from webapps.accounts.models import BemossAccount
from django.contrib.postgres.fields import JSONField

class DeviceType(models.Model):
    device_type = models.CharField(max_length=30) #system, thermostat, plugload, lighting

    class Meta:
        db_table = "device_type"

    def __unicode__(self):
        return str(self.as_json())

    def as_json(self):
        return dict(
            id=self.id,
            device_type=self.device_type.encode('utf-8').title())


class DeviceMetadata(models.Model):
    APPROVED = 'APR'
    NON_BEMOSS_DEVICE = 'NBD'
    PENDING = 'PND'

    APPROVAL_STATUS_CHOICES = (
        (APPROVED, 'Approved'),
        (PENDING, 'Pending'),
        (NON_BEMOSS_DEVICE, 'Non-BEMOSS Device')
    )

    agent_id = models.CharField(primary_key=True, max_length=50)
    device_type = models.ForeignKey(DeviceType)
    vendor_name = models.CharField(max_length=50,null=True)
    device_model = models.CharField(max_length=50,null=True)
    node = models.ForeignKey(NodeInfo)
    mac_address = models.CharField(max_length=300, null=True, blank=True)
    nickname = models.CharField(max_length=50,null=True,blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    config= JSONField(default={})
    identifiable = models.BooleanField(default=False)
    authorizable = models.BooleanField(default=False)
    communication = models.CharField(max_length=20,null=True)
    date_added = models.DateTimeField(null=True)
    approval_status = models.CharField(max_length=20,
                                       choices=APPROVAL_STATUS_CHOICES,
                                       default=PENDING)
    building = models.ForeignKey(BuildingInfo,null=False) # cannot be null
    account = models.ForeignKey(BemossAccount,null=False)
    zone = models.ForeignKey(ZoneInfo, null=True) # if null, the device is shown under all zones
    gateway = models.ForeignKey(IOTGateway,null=True)
    class Meta:
        db_table = "device_info"

    def __unicode__(self):
        return self.agent_id

    def as_json(self):
        return dict(
            agent_id=self.agent_id,
            device_type=self.device_type.device_type.encode('utf-8') if self.device_type else '',
            vendor_name=self.vendor_name.encode('utf-8') if self.vendor_name else '',
            device_model=self.device_model.encode('utf-8') if self.device_model else '',
            mac_address=self.mac_address.encode('utf-8') if self.mac_address else '',
            identifiable=self.identifiable,
            authorizable=self.authorizable,
            date_added=self.date_added,
            nickname = self.nickname,
            #bemoss=self.bemoss,
            approval_status=self.get_approval_status_display().encode('utf-8') if self.get_approval_status_display() else '',
            approval_status_choices=self.APPROVAL_STATUS_CHOICES)


    def data_dashboard(self):

        return dict(
            agent_id=self.agent_id,
            device_type=self.device_type.encode('utf-8') if self.device_type else '',
            vendor_name=self.vendor_name.encode('utf-8') if self.vendor_name else '',
            device_model=self.device_model.encode('utf-8') if self.device_model else '',
            device_model_id=self.device_model_id,
            mac_address=self.mac_address.encode('utf-8') if self.mac_address else '',
            identifiable=self.identifiable,
            config=self.config,
            authorizable=self.authorizable,
            #bemoss=self.bemoss,
            approval_status=self.approval_status,
            approval_status_choices=self.APPROVAL_STATUS_CHOICES)

    def device_control_page_info(self):
        return dict(
            agent_id=self.agent_id,
            # device_model_id=self.device_model_id,
            mac_address=self.mac_address.encode('utf-8') if self.mac_address else '',
            # device_type=self.device_type.encode('utf-8') if self.device_type else '',
            config=self.config,
            device_model=self.device_model,
            approval_status=self.approval_status)

    def device_status(self):
        return dict(
            device_model=self.device_model.encode('utf-8').capitalize() if self.device_model else '',
            date_added=self.date_added)


class SupportedDevices(models.Model):
    device_model = models.CharField(primary_key=True, max_length=50)
    vendor_name = models.CharField(max_length=50)
    communication = models.CharField(max_length=10)
    device_type = models.ForeignKey(DeviceType)
    api_name = models.CharField(max_length=50)
    html_template = models.CharField(max_length=50)
    chart_template = models.CharField(max_length=50, null=True)
    agent_type = models.CharField(max_length=50, default='BasicAgent')
    identifiable = models.BooleanField()
    authorizable = models.BooleanField(default=False)
    is_cloud_device = models.BooleanField(default=False)
    support_oauth = models.BooleanField(default=False)
    schedule_weekday_period = models.IntegerField(blank=True)
    schedule_weekend_period = models.IntegerField(blank=True)
    allow_schedule_period_delete = models.BooleanField(blank=True)
    built_in_schedule_support = models.BooleanField(default=False)
    address=models.CharField(max_length=300,null=True, default= "None")

    class Meta:
        db_table = "supported_devices"

    def __unicode__(self):
        return self.device_model

    def as_json(self):
        return dict(
            device_model=self.device_model,
            vendor_name=self.vendor_name,
            is_cloud_device=self.is_cloud_device,
            communiation = self.communication,
            device_type_id = self.device_type_id,
            device_type_name = self.device_type.device_type,
            address = self.address,
            identifiable = self.identifiable,
            authorizable = self.authorizable,
            html_template = self.html_template
        )

    def get_cloud_devices(self):
        return self.device_model

    def get_schedule_info(self):
        return dict(
            weekday_period=self.schedule_weekday_period,
            weekend_period=self.schedule_weekend_period,
            allow_delete=self.allow_schedule_period_delete,
            built_in=self.built_in_schedule_support
        )


class Miscellaneous(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    class Meta:
        db_table = "miscellaneous"

    def __unicode__(self):
        return self.id

    def as_json(self):
        return dict(
            key=self.key,
            value=self.value
        )

