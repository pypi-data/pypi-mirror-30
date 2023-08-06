import requests
import json
import yaml
import request



        
header= {'content-type': 'application/json'}

def  user(authtoken):      
        endpoint="/user"
        response = requests.get(
                request.client.url+endpoint,
                headers={'content-type': 'application/json',"Authorization":authtoken})
        output=yaml.load(json.dumps(response.json(),indent=2))
        if output["success"]==True:
                return output["data"]
        else:
                return "error"

def usersignup(username,password,firstName,lastName,country,address,city,state,nin,email,phone,birthdate):
        endpoint="/user/signup"
        rpc_input ={"username":username,"password":password,"firstName":firstName,"lastName":lastName,"country":country,"address":address,"city":city,"state":state,"nin":nin,"email":email,"phone":phone,"birthdate":birthdate,"overrideConfirmation":True}
        response = requests.post(
                   request.client.url+endpoint,data=json.dumps(rpc_input),
                   headers=header)
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return output["data"]["signupConfirmation"]
        else:
                return "error"

def signupverify(username,code):
        endpoint="/user/signup/verify"
        rpc_input = {"username": username, "code" : code}
        response = requests.post(
                request.client.url+endpoint,data=json.dumps(rpc_input),
                headers=header)
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return "True"
        else:
                return "error"

def signupresendconfirmation(username):
        endpoint="/user/signup/confirm"
        rpc_input = {"username": username}
        response = requests.post(
                request.client.url+endpoint,data=json.dumps(rpc_input),
                headers=header)
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return "True"
        else:
                return "error"

def userlogin(username,password):
        endpoint="/user/login"
        rpc_input = {"username": username, "password" : password}
        response = requests.post(
                request.client.url+endpoint,
                data=json.dumps(rpc_input),
                headers=header)
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                if output["data"]["twoFactorAuth"]==False:
                        return output["data"]["accessToken"]
                else:
                        return output["data"]["session"]
        else:
                return "error"

def userlogincode(username,code,session):
        endpoint="/user/login/code"
        rpc_input = {"username": username, "code" : code, "session":session}
        response = requests.post(
                request.client.url+endpoint,
                data=json.dumps(rpc_input),
                headers=header)
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return output["data"]["accessToken"]
        else:
                return "error"


def userforgotpassword(username):
        endpoint="/user/password"
        rpc_input = {"username": username}
        response = requests.post(
                request.client.url+endpoint,
                data=json.dumps(rpc_input),
                headers=header)
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return "Code Sent to:" , output["data"]["codeDestination"]
        else:
                return "error"


def userforgotpasswordconfirm(username,code,password):
        endpoint="/user/password/confirm"
        rpc_input = {"username": username,"code":code,"password":password}
        response = requests.post(
                request.client.url+endpoint,
                data=json.dumps(rpc_input),
                headers=header)
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return "True"
        else:
                return "error"



def userupdate(authtoken,data={}):
        
        endpoint="/user/update"
        headers = {'content-type': 'application/json',"Authorization":authtoken}
        rpc_input = data
        response = requests.put(
                request.client.url+endpoint,
                data=json.dumps(rpc_input),
                headers=headers)
        output=yaml.load(json.dumps(response.json()))
        if output["success"]==True:
                return output["data"]
        else:
                return "error"
