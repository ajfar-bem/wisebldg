import requests

pin="66NE6CEM"


import hashlib
import json
import os
import requests
import requests

url = "https://api.home.nest.com/oauth2/access_token"

payload = "code=66NE6CEM&client_id=7d7a95b7-53a6-4a90-bee2-35c9a6947b60&client_secret=GElta8GxB9CEICAwM2zJGwGDO&grant_type=authorization_code"

headers = {'content-type': 'application/x-www-form-urlencoded'}

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)





# url = "https://developer-api.nest.com/"
#
# token = "YOUR_TOKEN_HERE" # Update with your token
#
# headers = {'Authorization': 'Bearer {0}'.format(token), 'Content-Type': 'application/json'} # Update with your token
#
# initial_response = requests.get(url, headers=headers, allow_redirects=False)
# if initial_response.status_code == 307:
#     initial_response = requests.get(initial_response.headers['Location'], headers=headers, allow_redirects=False)
#
# print(initial_response.text)