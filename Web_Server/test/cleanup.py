import test_settings
import requests
import time
import getToken
import shutil
import settings

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE","django_web_server.settings_tornado")
from django_web_server import settings_tornado
django.setup()
from webapps.discovery.models import PasswordsManager
from webapps.device.models import DeviceMetadata, Devicedata
from webapps.schedule.models import schedule_data
from bemoss_lib.utils import misc_utils
from bemoss_lib.databases.cassandraAPI import cassandraDB

def cleanup():
    PasswordsManager.objects.all().delete()
    DeviceMetadata.objects.all().delete()
    Devicedata.objects.all().delete()
    schedule_data.objects.all().delete()
    cassandraDB.clearKeyspace()
    try:
        shutil.rmtree(settings.PROJECT_DIR+"/cassandra/data/data/bemossspace")
    except:
        pass


if __name__ == "__main__":
    cleanup()