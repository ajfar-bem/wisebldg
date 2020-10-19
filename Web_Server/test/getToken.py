import test_settings
import requests


def login(username, password):
    login_data = {"username":username,
              "password":password}

    url = test_settings.URL + "/api/login"
    result = requests.get(url,params=login_data)
    result.raise_for_status()
    resjosn = result.json()
    return resjosn['token']

if __name__=="__main__":
    print(login(test_settings.testusername, test_settings.testuserpassword))