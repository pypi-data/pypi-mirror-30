# import requests                 
# import json             
# import yaml
# import request   


# def  addexternalprovider(authtoken,provider,status,apiKey,apiSecret):
#         endpoint="/externalProvider"
#         rpc_input={"provider":provider,"status":status,"apiKey":apiKey,"apiSecret":apiSecret}
#         response = requests.post(
#                    request.client.url+endpoint,data=json.dumps(rpc_input),
#                    headers={'content-type': 'application/json',"Authorization":authtoken})
#         output=yaml.load(json.dumps(response.json()))
#         if output["success"]==True:
#                 return output["data"]
#         else:
#                 return "error"

# def  editexternalprovider(authtoken,status,apiKey,apiSecret):
#         endpoint="/externalProvider/yourprovider"
#         rpc_input={"provider":provider,"status":status,"apiKey":apiKey,"apiSecret":apiSecret}
#         response = requests.put(
#                    request.client.url+endpoint,data=json.dumps(rpc_input),
#                    headers={'content-type':'application/json',"Authorization":authtoken})
#         output=yaml.load(json.dumps(response.json()))
#         if output["success"]==True:
#                 return output["data"]
#         else:
#                 return "error"



# def delexternalprovider(authtoken,yourprovider):
#         endpoint="/externalProvider/" + yourprovider
#         response = requests.delete(
#                request.client.url+endpoint,
#                 headers={'content-type': 'application/json',"Authorization":authtoken})
#         output=yaml.load(json.dumps(response.json()))
#         if output["success"]==True:
#                 return output["data"]
#         else:
#                 return "error"


# def getexternalprovider(authtoken,yourprovider):
#         endpoint="/externalProvider"
#         response = requests.get(
#                 request.client.url+endpoint,
#                 headers={'content-type': 'application/json',"Authorization":authtoken})
#         output=yaml.load(json.dumps(response.json()))
#         if output["success"]==True:
#                 return output["data"]
#         else:
#                 return "error"


