# import requests
# import json
# import yaml
# import request




# def card(authtoken):
#         endpoint="/card" 
#         response = requests.get(
#                 request.client.url+endpoint,
#                 headers={'content-type': 'application/json',"Authorization": authtoken})
#         output=yaml.load(json.dumps(response.json()))
#         if output["success"]==True:
#                 return output["data"]["cards"]
#         else:
#                 return "error"

# def cardissue(authtoken):
#         endpoint="/card/issue" 
#         response = requests.post(
#                 request.client.url+endpoint,
#                 headers={'content-type': 'application/json',"Authorization": authtoken})
#         output=yaml.load(json.dumps(response.json()))
#         return output
#         # if output["success"]==True:
#         #         return output["data"]
#         # else:
#         #         return "error"


# def cardinfo(authtoken,san):
#         endpoint="/card/info" 
#         rpc_input = {"san" : san}
#         response = requests.post( 
#                  request.client.url+endpoint,data=json.dumps(rpc_input),
#                  headers={'content-type': 'application/json',"Authorization": authtoken})
#         output=yaml.load(json.dumps(response.json()))
#         return output
#         # if output["success"]==True:
#         #         return output["data"]
#         # else:
#         #         return "error"



# def cardactivate(authtoken):
#         endpoint="/card/activate" 
#         response = requests.get( 
#                  request.client.url+endpoint,
#                 headers={'content-type': 'application/json',"Authorization": authtoken})
#         output=yaml.load(json.dumps(response.json()))
#         if output["success"]==True:
#                 return output["data"]
#         else:
#                 return "error"



# def cardstatus(authtoken,san,bool):
#         endpoint="/card/status/" +san
#         rpc_input={"status":bool}
#         response = requests.get( 
#                 request.client.url+endpoint,
#                 data=json.dumps(rpc_input),
#                 headers={'content-type': 'application/json',"Authorization": authtoken})
#         output=yaml.load(json.dumps(response.json()))
#         if output["success"]==True:
#                 return output["data"]
#         else:
#                 return "error"
