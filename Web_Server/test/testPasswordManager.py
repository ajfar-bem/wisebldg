import test_settings
import getToken
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","django_web_server.settings_tornado")
from django_web_server import settings_tornado
django.setup()
from webapps.discovery.models import PasswordsManager

from addPassword import addPassword

def main(token):
    password_data = {"username": "bemosstester", "password": "Ari900_Ari900", "device_model": "RTH8580WF"}
    addPassword(token, password_data)
    PasswordsManager.objects.all().delete()
    return True

if __name__=="__main__":
    token = getToken.login(test_settings.testusername, test_settings.testuserpassword)
    main(token)