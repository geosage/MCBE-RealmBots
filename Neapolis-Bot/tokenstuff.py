from msal import PublicClientApplication
import requests
import json


def getxbl3(access_token, relyingparty):
    #XBOX LIVE TOKEN ------------------------------------------------------------------------------------------------------------------------------
    def send_xbox_auth_request(access_token):
        # Prepare the payload
        payload = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={access_token}"
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT"
        }

        # Send the POST request
        url = "https://user.auth.xboxlive.com/user/authenticate"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        # Process the response
        if response.status_code == 200:
            # Request successful
            formatted_response = json.dumps(response.json(), indent=4)
            return formatted_response
        else:
            # Request failed
            print("Request failed!")
            print("Status Code:", response.status_code)
            print("Error Message:", response.text)
            return None


    formatted_response = send_xbox_auth_request(access_token)
    data = json.loads(formatted_response)
    token = data["Token"]
    print(token)



    #XTXS TOKEN ----------------------------------------------------------------------------------------
    def send_xsts_authorize_request(xbl_token, relyingparty):
        # Prepare the payload
        payload = {
            "Properties": {
                "SandboxId": "RETAIL",
                "UserTokens": [
                    xbl_token
                ]
            },
            "RelyingParty": f"{relyingparty}",
            "TokenType": "JWT"
        }

        # Send the POST request
        url = "https://xsts.auth.xboxlive.com/xsts/authorize"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)

        # Process the response
        if response.status_code == 200:
            # Request successful
            formatted_response = json.dumps(response.json(), indent=4)
            return formatted_response
        else:
            # Request failed
            print("Request failed!")
            print("Status Code:", response.status_code)
            print("Error Message:", response.text)
            return None


    formatted_response = send_xsts_authorize_request(token, relyingparty)
    data = json.loads(formatted_response)
    token = data["Token"]
    uhs = data["DisplayClaims"]["xui"][0]["uhs"]

    xbl3token = f"XBL3.0 x={uhs};{token}"
    return xbl3token


#Refresh The Owners Access Token
def refreshtoken():

    with open('configs/realminfo.json') as temp_json_file:
        data = json.load(temp_json_file)

    refresh_token = data['refreshtoken']

    client_id = "9be57e9e-4bf2-4251-bb3c-0298d2bdda0a"
    scopes = ["Xboxlive.signin"]
    authority = "https://login.microsoftonline.com/consumers"

    pca = PublicClientApplication(client_id, authority=authority)



    # Acquire a new access token using the refresh token
    result = pca.acquire_token_by_refresh_token(refresh_token, scopes=scopes)

    if "access_token" in result:
        new_access_token = result["access_token"]
        newrealmstoken = getxbl3(new_access_token, "https://pocket.realms.minecraft.net/")
        newxblivetoken = getxbl3(new_access_token, "http://xboxlive.com")

        data['xblivetoken'] = newxblivetoken
        data['realmstoken'] = newrealmstoken

        with open('configs/realminfo.json', 'w') as temp_json_file:
            json.dump(data, temp_json_file, indent=4)

        print("Just refreshed the XBL3.0 Tokens!")
    else:
        print("An error occurred while refreshing the token.")
    
