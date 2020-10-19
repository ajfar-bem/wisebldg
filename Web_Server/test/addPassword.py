import test_settings
import requests
import logging
main_logger = logging.getLogger("testlogger")

def addPassword(token, password_data):
    main_logger.info("Trying to add password data")
    send_url = test_settings.URL + "/discovery/add_password_info_api"
    get_url = test_settings.URL + "/discovery/get_password_info_api"
    post_data= {}
    post_data['data'] = password_data
    token_dict = {'token': token}
    reply = requests.post(send_url, json=post_data, params=token_dict)
    reply.raise_for_status()
    result = requests.get(get_url, params=token_dict).json()
    result = result[0]
    for key, value in password_data.items():
        if result[key] != value:
            main_logger.error(key + " was not properly saved in the passwords table")
            raise Exception(key + " was not properly saved in the passwords table")
    return True
