import requests
import json
import yaml
import request



def getwallets(authtoken):
        endpoint="/wallet"
        response = requests.get(
                request.client.url+endpoint,
                headers={'content-type': 'application/json',"Authorization":authtoken})
        x=response.json()
        output=yaml.load(json.dumps(x,indent=2))
        if output["success"]==True:
                return output["data"]
        else:
                return "error"  

def generateaddress(authtoken,symbol):
        endpoint="/wallet/address/"+ symbol
        response = requests.get(
                        request.client.url+endpoint,
                        headers={'content-type': 'application/json',"Authorization":authtoken})
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return output["data"]["address"]
        else:
                return "error"  

def updatewallet(authtoken,symbol,isDefault):
        endpoint="/wallet/" + symbol
        rpc_input = {"isDefault":isDefault}
        response = requests.put(
                        request.client.url+endpoint,
                data=json.dumps(rpc_input),
                headers={'content-type': 'application/json',"Authorization":authtoken})
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return "True"
        else:
                return "error"
