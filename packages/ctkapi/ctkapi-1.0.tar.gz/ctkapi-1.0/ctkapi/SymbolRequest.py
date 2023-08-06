import requests
import json
import yaml
import request



    
def symbol(authtoken):
    endpoint="/symbol"
    response = requests.get(
                request.client.url+endpoint,
                headers={'content-type': 'application/json',"Authorization":authtoken})
    output=yaml.load(json.dumps(response.json()))
    if output["success"]==True:
            return output["data"]
    else:
            return "error"