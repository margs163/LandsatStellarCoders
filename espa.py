import json
import requests
from dotenv import load_dotenv
import os
load_dotenv()

HOST = 'https://espa.cr.usgs.gov/api'

username  = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

def espa_api(endpoint='', verb='get', body=None, uauth=None):
    """ Suggested simple way to interact with the ESPA JSON REST API """
    auth_tup = uauth if uauth else (username, password)
    response = getattr(requests, verb)(HOST + endpoint, auth=auth_tup, json=body)
    print('{} {}'.format(response.status_code, response.reason))
    data = response.json()
    if isinstance(data, dict):
        messages = data.pop("messages", None)  
        if messages:
            print((json.dumps(messages, indent=4)))
    try:
        print(response.raise_for_status())
    except Exception as e:
        print(e)
        return None
    else:
        return data

response = requests.get("https://espa.cr.usgs.gov/api/", auth=(username, password))
print(json.dumps(response.json(), indent=4))