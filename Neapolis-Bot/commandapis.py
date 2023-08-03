import requests
import json
import random
import discord
import time

def embedmake(title, color = "orange", thumbnail = False, footer = True):
    if color == "orange":
        embed = discord.Embed(
            title=f"{title}",
            color=discord.Colour.purple(),
        )
    elif color == "green":
        embed = discord.Embed(
            title=f"{title}",
            color=discord.Colour.green(),
        )
    elif color == "red":
        embed = discord.Embed(
            title=f"{title}",
            color=discord.Colour.red(),
        )
    
    if thumbnail != False:
        embed.set_thumbnail(url=thumbnail)
    
    if footer != False:
        embed.set_footer(
                text="Neapolis Realm Bot",
                icon_url='https://cdn.discordapp.com/attachments/960281633288765540/1135322918113517659/Untitled_Project.jpg'
            )
    return embed


def banembed(thumbnail, name, reason, duration, author, realms):
    banembed = embedmake(":no_entry_sign: Realm Ban", "red", thumbnail)

    #Gamertag, Reason
    banembedtext = f"> **Gamertag** - {name}\n> **Reason** - {reason}\n"

    #If Duration Specified
    if duration != None:
        #Convert time of unban to unix seconds
        unbantime = int(time.time()) + (duration * 3600 * 24)
        banembedtext = banembedtext + f"> **Duration** - {duration} day(s) (<t:{unbantime}:f>)\n"
    else: banembedtext = banembedtext + f"> **Duration** - Permanent\n"

    #Moderator, Realms
    banembedtext = banembedtext + f"> **Moderator** - {author.mention}\n > **Realms** - `{', '.join(realms)}`"
    
    banembed.add_field(
        name = "",
        value = banembedtext,
        inline = "False"
    )

    return banembed

def unbanembed(thumbnail, name, author, realms, reason="Ban Expired"):
    banembed = embedmake(":white_check_mark:  Realm Unban", "green", thumbnail)

    
    #Gamertag, Reason
    banembedtext = f"> **Gamertag** - {name}\n> **Reason** - {reason}\n"


    #Moderator, Realms
    banembedtext = banembedtext + f"> **Moderator** - {author.mention}\n > **Realms** - `{', '.join(realms)}`"
    
    banembed.add_field(
        name = "",
        value = banembedtext,
        inline = "False"
    )

    return banembed


#define the headers for basic mcpe api requests
def getrealmheaders():
    with open('configs/realminfo.json') as temp_json_file:
        realmstoken = json.load(temp_json_file)["realmstoken"]

    headers = {
            'Accept': '*/*',
            'authorization': f'{realmstoken}',
            'client-version': '1.17.10',
            'user-agent': 'MCPE/UWP',
            'Accept-Language': 'en-GB,en',
            'Accept-Encoding': 'gzip, deflate, be',
            'Host': 'pocket.realms.minecraft.net'
        }
    return headers

#define the headers for xblive api requests
def getxbliveheaders():
    with open('configs/realminfo.json') as temp_json_file:
        xblivetoken = json.load(temp_json_file)["xblivetoken"]

    headers = {
        "x-xbl-contract-version": "2",
        "content-type": "application/json",
        "Authorization": f"{xblivetoken}"
    }
    return headers

#converts a list of xuids into their names
def xuidstonames(xuidlist, count = 0):
    headers = getxbliveheaders()
    payload = {
        "userIds": xuidlist,
        "settings": [
            "GameDisplayName"
        ]
    }
    url = "https://profile.xboxlive.com/users/batch/profile/settings"
    response = requests.request("POST", url, headers=headers, json=payload)

    #sort through the json data and replace their xuid with there gamertag
    jsondata = response.json()
    for user in jsondata["profileUsers"]:
        xuidlist[count] = user["settings"][0]["value"]
        count += 1
    return xuidlist

#convert a gamertag into their xuid
def nametoxuid(name, picneeded = False):
    headers = getxbliveheaders()
    url = f'https://profile.xboxlive.com/users/gt({name})/profile/settings?settings=GameDisplayPicRaw'
    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    
    #check if the user exists
    if response.status_code == 200:
        data = response.json()
        name = data["profileUsers"][0]["id"]
        gamerpic = data["profileUsers"][0]["settings"][0]["value"]
        if picneeded == True:
            return name, gamerpic
        else:
            return name
    else: return False
    
def getrealmconnection(realmid):
    headers = getrealmheaders()
    url = f'https://pocket.realms.minecraft.net/worlds/{realmid}/join'
    data = {}

    # Send request
    response = requests.request("GET", url, headers=headers, data=data)

    # Parse the JSON data to get realms the user owns
    jsondata = response.json()
    print(jsondata)
    print("address:")
    address = jsondata["address"].split(":")
    print(address)
    ip = address[0]
    port = address[1]

    return ip, port

#Refresh The Realms The User Owns And Return Their Names
def refreshrealms():
    realmcount = 0
    realms = []
    realmids = []
    
    headers = getrealmheaders()
    url = 'https://pocket.realms.minecraft.net/worlds'
    data = {}
    # Send request
    response = requests.request("GET", url, headers=headers, data=data)
    print(response.content)

    # Get owner id
    with open('configs/realminfo.json', 'r') as temp_json_file:
        data = json.load(temp_json_file)
        ownerxuid = data["ownerxuid"]
    
    # Parse the JSON data to get realms the user owns
    jsondata = response.json()
    for realm in jsondata["servers"]:# Add Something here which makes sure that the realms are in the correct order. (Ask the owner which order they want)
        if realm["ownerUUID"] == ownerxuid and realm["state"] == "OPEN": # Also. Make it so it resets all the other parameters such as console.
            realmcount += 1
            # Set all the json keys
            data[f"realm{realmcount}"]["name"] = realm["name"]
            data[f"realm{realmcount}"]["realmid"] = realm["id"]
            data[f"realm{realmcount}"]["relayenabled"] = "False"
            data[f"realm{realmcount}"]["relaychannel"] = 0
            data[f"realm{realmcount}"]["cmdlogsenabled"] = "False"
            data[f"realm{realmcount}"]["cmdlogschannel"] = 0
            data[f"realm{realmcount}"]["joinlogsenabled"] = "False"
            data[f"realm{realmcount}"]["joinlogschannel"] = 0
            data[f"realm{realmcount}"]["codechange"] = "False"
            data[f"realm{realmcount}"]["alwaysingame"] = "False"
    data["realmcount"] = realmcount

    # Write the updated data back to the file
    with open('configs/realminfo.json', 'w') as temp_json_file:
        json.dump(data, temp_json_file, indent=4)
    return realms, realmids


#Get The Online Players For Each Realm And Return The Embed
def realmplayers(realmids):
    count = len(realmids)
    playercount = 0

    playersembed = embedmake("Online Players")

    headers = getrealmheaders()
    url = 'https://pocket.realms.minecraft.net/activities/live/players'
    data = {}
    # Send request
    response = requests.request("GET", url, headers=headers, data=data)

    # Parse the JSON data to get realms the user owns
    with open('configs/realminfo.json') as temp_json_file:
        realmdata = json.load(temp_json_file)

        #go through the realms list
        jsondata = response.json()
        for id in realmids:
            for realm in jsondata["servers"]:
                if realm["id"] == id:
                    playerxuids = []
                    textforembed = ""
                    position = realmids.index(id)
                    realmname = f"{realmdata[f'realm{position+1}']['name']}"
                    for player in realm["players"]:
                        if player['uuid'] != "":
                            playerxuids.append(player['uuid'])
                    #convert xuids to names
                    names = xuidstonames(playerxuids)
                    #add to the embed
                    for name in names:
                        index = names.index(name) + 1
                        textforembed = textforembed + f"**{index}.** {name}\n"
                    textforembed = f"{index}/11 Players\n" + textforembed + "----------------------------"
                    playersembed.add_field(
                        name=f"{realmname}",
                        value=f"{textforembed}",
                        inline="False"
                    )

        return playersembed

#Invite, Ban, Unban, Permission ----------------------------------------------------------------------------------------------------
#Invite
def realminvite(xuid, realmid):
    headers = getrealmheaders()
    payload = {
        "invites": { f"{xuid}": "ADD"} 
    }
    url = f'https://pocket.realms.minecraft.net/invites/{realmid}/invite/update'
    
    #send request
    requests.request("PUT", url, headers=headers)
    print(f"just invited {xuid}")

#Ban
def realmban(xuid, realmid):
    headers = getrealmheaders()
    url = f'https://pocket.realms.minecraft.net/worlds/{realmid}/blocklist/{xuid}'

    #send request
    requests.request("POST", url, headers=headers)
    print(f"just banned {xuid}")

#Unban
def realmunban(xuid, realmid):
    headers = getrealmheaders()
    url = f'https://pocket.realms.minecraft.net/worlds/{realmid}/blocklist/{xuid}'

    #send request
    requests.request("DELETE", url, headers=headers)
    print(f"just unbanned {xuid}")

#Permission
def realmpermission(xuid, realmid, permission):
    headers = getrealmheaders()
    payload = {
        "permission": f"{permission}",
        "xuid": f"{xuid}"
    }

    url = f'https://pocket.realms.minecraft.net/worlds/{realmid}/userPermission'

    
    #send request
    requests.request("PUT", url, headers=headers, json=payload)
    print(f"just changed {xuid}'s permissions to {permission}")

#Rename
def realmrename(name, realmid):
    headers = getrealmheaders()
    payload = {
        "name": f"{name}",
    }
    url = f'https://pocket.realms.minecraft.net/worlds/{realmid}'

    #send request
    requests.request("POST", url, headers=headers, json=payload)
    print(f"just renamed a realm to {name}")

#Open/Close
def realmopenclose(realmid, option):
    headers = getrealmheaders()
    url = f'https://pocket.realms.minecraft.net/worlds/{realmid}/{option}'

    #send request
    requests.request("PUT", url, headers=headers)
    print(f"just {option}ed a realm")