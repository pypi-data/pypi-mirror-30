import requests
import json
import yaml 
import request


        
def  exchangetransactions(authtoken):
        endpoint="/exchange/transactions"
        response = requests.get(
               request.client.url+endpoint,
                headers={'content-type': 'application/json',"Authorization":authtoken})
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return output["data"]
        else:
                return "error"

def exchange(authtoken):
        endpoint="/exchange"
        response = requests.get(
               request.client.url+endpoint,
                headers={'content-type': 'application/json',"Authorization":authtoken})
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return output["data"]
        else:
                return "error"



def exchangeid(authtoken,id):
        endpoint="/exchange/" + id
        response = requests.get(
                request.client.url+endpoint,
                headers={'content-type': 'application/json',"Authorization":authtoken})
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return output["data"]
        else:
                return "error"


def exchangeminimum(authtoken,fromasset,toasset):
        endpoint="/exchange/minimum"
        rpc_input={"from":fromasset,"to":toasset}
        response = requests.post(
                request.client.url+endpoint,
                data=json.dumps(rpc_input),
                headers={'content-type': 'application/json',"Authorization":authtoken})
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return output["data"]
        else:
                return "error"


def exchangetransaction(authtoken,fromasset,toasset,amount):
        endpoint="/exchange/transaction"
        rpc_input={"from":fromasset,"to":toasset,"amount":amount}
        response = requests.post(
                request.client.url+endpoint,
                data=json.dumps(rpc_input),
                headers={'content-type': 'application/json',"Authorization":authtoken})
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return output["data"]
        else:
                return "error"
