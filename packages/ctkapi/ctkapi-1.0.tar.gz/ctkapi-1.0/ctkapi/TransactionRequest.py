import requests
import yaml
import json
import request


def transactionbysymbol(authtoken,symbol,page,limit):
    endpoint="/transactionBySymbol?page="+page+"&"+"limit="+limit+"&"+"symbol="+symbol
    response = requests.get(
                request.client.url+endpoint,
                headers={'content-type': 'application/json',"Authorization":authtoken})
    output=yaml.load(json.dumps(response.json()))
    if output["success"]==True:
            return output["data"]
    else:
            return "error"

def transaction(authtoken,page,limit):
    endpoint="/transaction?page="+page+"&"+"limit="+limit
    response = requests.get(
               request.client.url+endpoint,
                headers={'content-type': 'application/json',"Authorization":authtoken})
    output=yaml.load(json.dumps(response.json()))
    if output["success"]==True:
            return output["data"]
    else:
            return "error"

def transactiontotal(authtoken,type,period,symbol):
    endpoint="/transaction/total?type="+type+"&period="+period+"&symbol="+symbol
    response = requests.get(
               request.client.url+endpoint,
               headers={'content-type': 'application/json',"Authorization":authtoken})
    output=yaml.load(json.dumps(response.json()))
    if output["success"]==True:
            return output["data"]
    else:
            return "error"