from test import getEmails, test_settings
import requests
import time
import getToken

def main(token):
    account_creation_data = {u'owner_name': [u'owner1'], u'contract_id': [u'contract1'], u'owner_email': [u'bemosstesting@gmail.com'],
                             u'applicationchecks': [u'Plugload_Scheduler', u'Lighting_Scheduler', u'Iblc', u'Fault_Detection',
                                                    u'Thermostat_Control', u'Dr_Test'], u'device_limit': [u'10'],
                             u'csrfmiddlewaretoken': [u'cxfqZtyV9DlTRQ5JJnGLAztSgsSm7hukjJFYx8f9S2pl6CNlym8bJ47crAnLmfkZ'],
                             u'buildinglist': [u'Building1', u'Building2'], u'account_name': [u'account1'], u'devicechecks':
                                 [u'Hvac', u'Lighting', u'Plugload', u'Sensor', u'Powermeter', u'Der', u'Camera']}

    post_data = dict()
    post_data['data'] = account_creation_data
    url = test_settings.URL + "/accounts/add_account_api"
    data  = {}
    reply = requests.post(url,params={"token":token},json=post_data)
    reply.raise_for_status()
    email = ""
    time.sleep(2)
    recheck_count = 10
    while recheck_count:
        email = getEmails(subject="BEMOSS User Activation Token")
        if not email:
            recheck_count -= 1
            time.sleep(2)
        else:
            print(email[0])
            break

    if not email:
        raise Exception("Email never recieved")

if __name__=="__main__":
    token = getToken.login(test_settings.testusername, test_settings.testuserpassword)
    main(token)