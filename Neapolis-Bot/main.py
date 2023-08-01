#Import Stuff
import discord
from discord.ext import tasks
import os
from dotenv import load_dotenv
import tokenstuff
import commandapis as cmds
import ingamebot
import json
import sqlite3
import time

from javascript import require, On
bedrock = require('bedrock-protocol')


clients = {}
chatrelaychannels = []

def createclient(ip, port):
    try:
        botclient = bedrock.createClient({
                'host': ip,
                'port': int(port),
                'profilesFolder': "./authCache",
                'skipPing': True,
                'skinData': {
                    'CurrentInputMode': 3,
                    'DefaultInputMode': 3,
                    'DeviceModel': 'Xbox Series X',
                    'DeviceOS': 11
                }
            })
        return botclient
    except Exception as e:
        print(f"Connection attempt failed: {e}")
        return None
        


def makebotjoin(realmid, index):
    try:
        # Get the IP and port of the realm
        ip, port = cmds.getrealmconnection(realmid)

        # Create the client and store it in the dictionary with the realm index as the key
        client = createclient(ip, port)
        if client != None:
            clients[index] = client # With this clients index thing. Have it so when there is a disconnect event it deletes the client id by causing a function over here or just updating. Ask ChatGPT


            with open('configs/realminfo.json') as temp_json_file:
                data = json.load(temp_json_file)

                # Check if the things are enabled
                if data[f"realm{index}"]["relayenabled"] == "True":
                    relaychannel = data[f"realm{index}"]["relaychannel"] 
                else: relaychannel = False

                if data[f"realm{index}"]["cmdlogsenabled"] == "True":
                    cmdlogschannel = data[f"realm{index}"]["cmdlogschannel"]
                else: cmdlogschannel = False

                if data[f"realm{index}"]["joinlogsenabled"] == "True":
                    joinlogschannel = data[f"realm{index}"]["joinlogschannel"]
                else: joinlogschannel = False


            # Start the Bot Up
            ingamebot.start(client, bot, relaychannel, joinlogschannel, cmdlogschannel)
        else:
            return
    except Exception as e:
        print(f"An error occured: {e}")
        return



#Database stuff
conn = sqlite3.connect('bans.db')
c = conn.cursor()


global realmnames, realmids
realmnames = []
realmids = []

load_dotenv()


bot = discord.Bot(debug_guilds=[960278336897179758], intents=discord.Intents.all())

#Load the permissions
permissionslist = []
with open('configs/commandperms.json') as temp_json_file:
    data = json.load(temp_json_file)
    for key in data:
        permissionslist.append(key)

#Create the command groups -------------------------------------------------------
realmcmds = bot.create_group(
    "realm", "Commands related to the realm"
)

permissioncmds = bot.create_group(
    "permissons", "Commands related to the permissions"
)

configcmds = bot.create_group(
    "config", "Commands related to the config"
)

botcmds = bot.create_group(
    "bot", "Commands related to the bot"
)


#checks If the user has permission to run the command
async def checkperms(ctx, cmdtype):
    user = ctx.author

    #get the users roles ids
    users_roles = []
    for role in user.roles:
        users_roles.append(role.id)

    #load the config file and extract data
    with open('configs/commandperms.json') as temp_json_file:
        data = json.load(temp_json_file)
    roleswithperm = data[cmdtype]

    #check if the user has the perms
    if any(item in users_roles for item in roleswithperm) or user.id == 614570887160791050:
        return True
    else:
        await ctx.respond("You do not have permission to run this command!", ephemeral=True)
        return False
        
#get the names and ids of the realms
def checknames():
    realmnames = []
    realmids = []

    with open('configs/realminfo.json') as temp_json_file:
        data = json.load(temp_json_file)

        for i in range(data["realmcount"]):
            realmnames.append(data[f"realm{i+1}"]["name"])
            realmids.append(data[f"realm{i+1}"]["realmid"])

    return realmnames, realmids
realmnames, realmids = checknames()

#Misc Commands ---------------------------------------------------------------------------------------
@bot.slash_command(name="rolelist", description="server roles innit")
async def queryinvites(ctx):
    print(ctx.guild.roles)

@bot.slash_command(name="refreshrealms", description="Refresh Your Realm List")
async def queryinvites(ctx):
    message = ""

    if (await checkperms(ctx, "refreshrealms")):
        realms, realmids = cmds.refreshrealms()

        for i in realms:
            message = message + i + ", "
        await ctx.respond(f"Successfully refreshed {message}")


#Realm Commands ---------------------------------------------------------------------------------------------------------------------------------------
#Realm Players
@realmcmds.command(name="players", description="Get a list of currently online members")  
async def players(ctx):
    realmids = []

    if (await checkperms(ctx, "players")):
        #open the json
        with open('configs/realminfo.json') as temp_json_file:
            data = json.load(temp_json_file)
            realmcount = data["realmcount"]

            #iterate through realms
            for i in range(realmcount):
                realmids.append(data[f"realm{i+1}"]["realmid"])

        #call the function for api
        playersembed = cmds.realmplayers(realmids)
        await ctx.respond(embed=playersembed)

#Realm Invite
@realmcmds.command(name="invite", description="Invites a user to the realm")  
async def players(ctx, user: discord.Option(str, description="The Gamertag to invite"), realm: discord.Option(str, choices=realmnames, description="The Realm to invite them to", required=False)):
    realmids = []

    if (await checkperms(ctx, "invite")):
        #turn name to xuid
        xuid = cmds.nametoxuid(user)
        #get the realms to invite them to
        if xuid != False:
            #get the realms to ban them on
            if realm:
                index = realmnames.index(realm)
                realmid = realmids[index]
                cmds.realminvite(xuid, realmid)
            else:
                for realmid in realmids:
                    cmds.realminvite(xuid, realmid)

            await ctx.respond(f"Successfully invited {user}")
        else:
            await ctx.respond("This user does not exist.")

#Realm Ban
@realmcmds.command(name="ban", description="Bans a user from the realm")  
async def players(ctx, user: discord.Option(str, description="The Gamertag to ban"), reason: discord.Option(str, description="The Reason for the ban"), duration: discord.Option(int, description="The Length of the ban in days", required=False), realm: discord.Option(str, choices=realmnames, description="The Realm to ban them on", required=False)):

    if (await checkperms(ctx, "ban")):
        author = ctx.author

        #turn name to xuid
        xuid, gamerpic = cmds.nametoxuid(user, True)
        realmstoban = []
        if xuid != False:
            #get the realms to ban them on
            if realm:
                index = realmnames.index(realm)
                realmid = realmids[index]

                realmstoban.append(realm)
                cmds.realmban(xuid, realmid)
            else:
                realmstoban = realmnames
                for realmid in realmids:
                    cmds.realmban(xuid, realmid)
            

            embedtosend = cmds.banembed(gamerpic, user, reason, duration, author, realmstoban)
            
            #If duration specified add to ban database or edit
            if duration != None:
                #If duration is less than 1 say they cant do it
                if duration < 1:
                    await ctx.respond(f"Successfully banned {user} for {reason}. This ban is permanent since the duration specified was less than 1.")
                    return
                else:
                    bantime = int(time.time())
                    unbantime = bantime + (duration * 3600 * 24)

                    c.execute('SELECT xuid FROM bans WHERE xuid = ?', (xuid,))
                    check = c.fetchone()

                    #Check if they are already in there
                    if check:
                        c.execute('UPDATE bans SET unbantime = ? WHERE xuid = ?', (unbantime, xuid))
                    #If they arent already in database then add them to it
                    else:
                        c.execute('INSERT INTO bans (gamertag, gamerpic, xuid, bantime, unbantime) VALUES (?, ?, ?, ?, ?)', (user, gamerpic, xuid, bantime, unbantime))
                    
            #Else Remove from ban database if in there as its now permanent
            else:
                c.execute('DELETE FROM bans WHERE xuid = ?', (xuid,))

            conn.commit()

            #Send Embed and Message
            with open('configs/channels.json') as temp_json_file:
                data = json.load(temp_json_file)
                banchannel = bot.get_channel(data["ban"])
            
            await banchannel.send(embed=embedtosend)
            await ctx.respond(f"Successfully banned {user} for {reason}")
        else:
            await ctx.respond("This user does not exist.")

#Realm Unban
@realmcmds.command(name="unban", description="Unbans a user from the realm")  
async def players(ctx, user: discord.Option(str, description="The Gamertag to unban"), reason: discord.Option(str, description="The Reason for the unban"), realm: discord.Option(str, choices=realmnames, description="The Realm to unban them on", required=False)):

    if (await checkperms(ctx, "unban")):
        author = ctx.author

        #turn name to xuid
        xuid, gamerpic = cmds.nametoxuid(user, True)
        realmstounban = []
        if xuid != False:
            #get the realms to unban them on
            if realm:
                index = realmnames.index(realm)
                realmid = realmids[index]

                realmstounban.append(realm)
                cmds.realmunban(xuid, realmid)
            else:
                realmstounban = realmnames
                for realmid in realmids:
                    cmds.realmunban(xuid, realmid)

            #Remove them from the ban database if they are in there
            c.execute('DELETE FROM bans WHERE xuid = ?', (xuid,))
            conn.commit()

            embedtosend = cmds.unbanembed(gamerpic, user, author, realmstounban, reason)
            with open('configs/channels.json') as temp_json_file:
                data = json.load(temp_json_file)
                unbanchannel = bot.get_channel(data["unban"])

            await unbanchannel.send(embed=embedtosend)
            await ctx.respond(f"Successfully unbanned {user}")
        else:
            await ctx.respond("This user does not exist.")

#Realm Permission
@realmcmds.command(name="permission", description="Update a users permissions")  
async def players(ctx, user: discord.Option(str, description="The Gamertag to change permissions"), permission: discord.Option(str, choices=["VISITOR", "MEMBER", "OPERATOR"], description="The Permission to set them to"), realm: discord.Option(str, choices=realmnames, description="The Realm to change their permissions on", required=False)):

    if (await checkperms(ctx, "permission")):
        #turn name to xuid
        xuid = cmds.nametoxuid(user)
        if xuid != False:
            #get the realms to change permission on
            if realm:
                index = realmnames.index(realm)
                realmid = realmids[index]
                cmds.realmpermission(xuid, realmid, permission)
            else:
                for realmid in realmids:
                    cmds.realmpermission(xuid, realmid, permission)
            await ctx.respond(f"Successfully changed {user}'s permission to {permission}")
        else:
            await ctx.respond("This user does not exist.")

#Realm Rename
@realmcmds.command(name="rename", description="Change the name of a realm")  
async def players(ctx, name: discord.Option(str, description="The Name you want to change it to"), realm: discord.Option(str, choices=realmnames, description="The Realm to change the name of")):

    if (await checkperms(ctx, "rename")):
        #get the realm to change the name of
        index = realmnames.index(realm)
        realmid = realmids[index]
        cmds.realmrename(name, realmid)
        await ctx.respond(f"Successfully renamed {realm} to {name}")

#Realm Open
@realmcmds.command(name="open", description="Open a realm")  
async def players(ctx, realm: discord.Option(str, choices=realmnames, description="The Realm you want to open", required=False)):

    if (await checkperms(ctx, "open")):
        #get the realms to open
        if realm:
            index = realmnames.index(realm)
            realmid = realmids[index]
            cmds.realmopenclose(realmid, "open")
        else:
            for realmid in realmids:
                cmds.realmopenclose(realmid, "open")
        await ctx.respond(f"Successfully changed opened the realm")

#Realm Close
@realmcmds.command(name="close", description="Close a realm")  
async def players(ctx, realm: discord.Option(str, choices=realmnames, description="The Realm you want to close", required=False)):

    if (await checkperms(ctx, "close")):
        #get the realms to open
        if realm:
            index = realmnames.index(realm)
            realmid = realmids[index]
            cmds.realmopenclose(realmid, "close")
        else:
            for realmid in realmids:
                cmds.realmopenclose(realmid, "close")
        await ctx.respond(f"Successfully closed the realm")

# --------------------------------------------------------------------------------------------------------------------------------------

#Permissions Commands ----------------------------------------------------------------------------------------------------------------------------------------
#Permissions List
@permissioncmds.command(name="view", description="View the permissions for this guild")  
async def players(ctx):

    if (await checkperms(ctx, "permissionsview")):
        with open('configs/commandperms.json') as temp_json_file:
            data = json.load(temp_json_file)
            
            #sort through the json and replace the ids with their names
            for key, value_list in data.items():
                updated_value_list = []
                for roleid in value_list:
                    role = discord.utils.get(ctx.guild.roles, id=roleid)
                    if role:
                        updated_value_list.append(role.name)
                data[key] = updated_value_list
            await ctx.respond(f"```json\n{json.dumps(data, indent=4, ensure_ascii=False)}\n```")

#Permissions Add
@permissioncmds.command(name="add", description="Add a permission for a role")  
async def players(ctx, permission: discord.Option(str, choices=permissionslist, description="The Permission to give the role"), role: discord.Option(discord.Role, description="The Role to add the permission to")):

    if (await checkperms(ctx, "permissionsadd")):
        with open('configs/commandperms.json') as temp_json_file:
            data = json.load(temp_json_file)
            #add to the permission roleids
            data[permission].append(role.id)

        #write to the json file
        with open('configs/commandperms.json', 'w') as temp_json_file:
            json.dump(data, temp_json_file, indent=4)
        await ctx.respond(f"Just gave the permission '{permission}' to {role.name}")

#Permissions Remove
@permissioncmds.command(name="remove", description="Remove a permission for a role")  
async def players(ctx, permission: discord.Option(str, choices=permissionslist, description="The Permission to remove from the role"), role: discord.Option(discord.Role, description="The Role to remove the permission from")):

    if (await checkperms(ctx, "permissionsremove")):
        with open('configs/commandperms.json') as temp_json_file:
            data = json.load(temp_json_file)
            #check if the role has that permission
            if role.id in data[permission]:
                #remove from the permission roleids
                data[permission].remove(role.id)
                await ctx.respond(f"Just removed the permission '{permission}' from {role.name}")
            else:
                await ctx.respond(f"{role.name} does not have the permission '{permission}'")

        #write to the json file
        with open('configs/commandperms.json', 'w') as temp_json_file:
            json.dump(data, temp_json_file, indent=4)

#Config --- One commandperm for all --------------------------------------------------------------------------------------------------------------

#Config View {Shows all the configs}



#Config Logs {All Optional. They just select the channel. (Ban, Unban, Automod)}
@configcmds.command(name="logs", description="Set the channel for the logs")  
async def players(ctx, type: discord.Option(str, choices=["Ban", "Unban", "Automod"], description="The Logs type to set"), channel: discord.Option(discord.TextChannel, description="The Channel to set it in")):

    if (await checkperms(ctx, "configcommands")):
        with open('configs/channels.json') as temp_json_file:
            data = json.load(temp_json_file)

            #Find what type is equal to
            if type == "Ban":
                data["ban"] = channel.id
            elif type == "Unban":
                data["unban"] = channel.id
            elif type == "Automod":
                data["automod"] = channel.id
        #Write new config to file
        with open('configs/channels.json', 'w') as temp_json_file:
            json.dump(data, temp_json_file, indent=4)
        await ctx.respond(f"Just set {type} logs to {channel.name}")

#Config Bot {Channels (Realm, Chatrelay, CommandLogs, Console, JoinLogs)}
@configcmds.command(name="bot", description="Set the channels for the bot relay")  
async def players(ctx, type: discord.Option(str, choices=["ChatRelay", "CommandLogs", "Joins/Leaves"], description="The Relay type to set"), realm: discord.Option(str, choices=realmnames, description="The Realm you want to set the relay for"), channel: discord.Option(discord.TextChannel, description="The Channel to set it in")):

    if (await checkperms(ctx, "configcommands")):
        with open('configs/realminfo.json') as temp_json_file:
            data = json.load(temp_json_file)
            index = realmnames.index(realm) + 1

            #Find what type is equal to
            if type == "ChatRelay":
                data[f"realm{index}"]["relaychannel"] = channel.id
            elif type == "CommandLogs":
                data[f"realm{index}"]["cmdlogschannel"] = channel.id
            elif type == "Joins/Leaves":
                data[f"realm{index}"]["joinlogschannel"] = channel.id

        #Write new config to file
        with open('configs/realminfo.json', 'w') as temp_json_file:
            json.dump(data, temp_json_file, indent=4)
        await ctx.respond(f"Just set {type} logs to {channel.name}")

#Config Messages (Ban, Unban)
@configcmds.command(name="messages", description="Set the messages to send to users")  
async def players(ctx, type: discord.Option(str, choices=["Ban", "Unban"], description="The Type to set the message for"), message: discord.Option(str, description="The Message to send")):

    if (await checkperms(ctx, "configcommands")):
        with open('configs/messages.json') as temp_json_file:
            data = json.load(temp_json_file)

            #Find what type is equal to
            if type == "Ban":
                data["ban"] = message
            else:
                data["unban"] = message
        #Write new config to file
        with open('configs/messages.json', 'w') as temp_json_file:
            json.dump(data, temp_json_file, indent=4)
        await ctx.respond(f"Just set the {type} message to '{message}'")

#Config Automod {All Optional. (Gamerscore, Device) # Might Do AutoMod --------------------------------------------------


#Bot --------------------------------------------------------------------------------------------------------------------
#Bot Join (Realm)
@botcmds.command(name="join", description="Makes the bot join a realm")  
async def players(ctx, realm: discord.Option(str, choices=realmnames, description="The realm to join")):

    if (await checkperms(ctx, "bottoggle")):
        with open('configs/realminfo.json') as temp_json_file:
            data = json.load(temp_json_file)
            index = realmnames.index(realm) + 1

            realmidtojoin = data[f"realm{index}"]["realmid"]

        makebotjoin(realmidtojoin, index)

        await ctx.respond(f"The Bot is joining {realm}")

#Bot Leave (Realm)
@botcmds.command(name="leave", description="Makes the bot leave a realm")  
async def players(ctx, realm: discord.Option(str, choices=realmnames, description="The realm to leave")):

    if (await checkperms(ctx, "bottoggle")):
        with open('configs/realminfo.json') as temp_json_file:
            data = json.load(temp_json_file)
            index = realmnames.index(realm) + 1

        #Get the client for that realm
        if index in clients:
            clients[index].disconnect()
            clients.pop(index)

            await ctx.respond(f"Just disconnected the bot from {realm}")
        else:
            await ctx.respond(f"The bot is not currently in {realm}")

#Bot Send (Command, Realm)
@botcmds.command(name="send", description="Makes the bot send a message/command")  
async def players(ctx, message: discord.Option(str, description="The Message/Command to send"), realm: discord.Option(str, choices=realmnames, description="The realm to send it on")):

    if (await checkperms(ctx, "botsend")):
        with open('configs/realminfo.json') as temp_json_file:
            data = json.load(temp_json_file)
            index = realmnames.index(realm) + 1

        #Send the text as the client
        if index in clients:
            if message[:1] == '/':
                clients[index].queue('command_request', {
                    'command': message,
                    'origin': { 'type': 'player', 'uuid': '', 'request_id': '', },
                    'internal': False,
                    'version': 70
                })
            else:
                clients[index].queue('text', {
                    'type': 'chat',
                    'needs_translation': False,
                    'source_name': clients[index].username,
                    'xuid': '',
                    'platform_chat_id': '',
                    'message': message
                })
            
            await ctx.respond(f"Successfully sent `{message}` to {realm}")
            
        else:
            await ctx.respond(f"The bot is not currently in {realm}")

#Bot Toggle (Realm, {AlwaysInGame, Chatrelay, CommandLogs, Automod, JoinLogs, CodeChange} {True/False}) # Might Do AutoMod --------------------------------------------------
@botcmds.command(name="toggle", description="Toggle settings about the bot")  
async def players(ctx, type: discord.Option(str, choices=["AlwaysInGame", "ChatRelay", "CommandLogs", "JoinLogs", "CodeChange"], description="The Setting to toggle"), check: discord.Option(str, choices=["True", "False"], description="True or False"), realm: discord.Option(str, choices=realmnames, description="The Realm you want to toggle it on")):

    if (await checkperms(ctx, "bottoggle")):
        with open('configs/realminfo.json') as temp_json_file:
            data = json.load(temp_json_file)
            index = realmnames.index(realm) + 1

            #Find what type is equal to
            if type == "AlwaysInGame":
                data[f"realm{index}"]["alwaysingame"] = check
            elif type == "ChatRelay":
                data[f"realm{index}"]["relayenabled"] = check
            elif type == "CommandLogs":
                data[f"realm{index}"]["cmdlogsenabled"] = check
            elif type == "JoinLogs":
                data[f"realm{index}"]["joinlogsenabled"] = check
            elif type == "CodeChange":
                data[f"realm{index}"]["codechange"] = check

        #Write new config to file
        with open('configs/realminfo.json', 'w') as temp_json_file:
            json.dump(data, temp_json_file, indent=4)
        await ctx.respond(f"Just set {type} to '{check}' for {realm}")
            

#Loops ------------------------------------------------------------------------------------------------------------------------
#Setup Loop to reset the Token every 12 hours
@tasks.loop(hours=12)
async def refrestokentimer():
    print("Started Refreshing the XBL3.0 Token!")
    tokenstuff.refreshtoken()

#Setup loop to unban every 1 hour
@tasks.loop(hours=1)
async def unbantimer():
    currenttime = int(time.time())
    print("Starting Unbans")
    
    #Select all from database and iterate over them
    c.execute('SELECT * FROM bans')
    for record in c.fetchall():
        unbantime = record[4]
        
        #If their ban has expired
        if currenttime > unbantime:
            user = record[0]
            gamerpic = record[1]
            xuid = record[2]
            author = bot.user
            realmstounban = realmnames
            reason = 'Ban Expired'

            #Iterate through realms and unban from all
            for realmid in realmids:
                cmds.realmunban(xuid, realmid)

            #Remove them from the ban database if they are in there
            c.execute('DELETE FROM bans WHERE xuid = ?', (xuid,))
            conn.commit()

            #Make the unban embed and send it
            embedtosend = cmds.unbanembed(gamerpic, user, author, realmstounban, reason)
            with open('configs/channels.json') as temp_json_file:
                data = json.load(temp_json_file)
                unbanchannel = bot.get_channel(data["unban"])

            await unbanchannel.send(embed=embedtosend)



#Setup loop to run every 1 minute
@tasks.loop(minutes=2)
async def tenminutetimer():
    global chatrelaychannels
    chatrelaychannels = []

    #Update things like chatrelay channels
    with open('configs/realminfo.json') as temp_json_file:
        data = json.load(temp_json_file)

        #Set the chatrelaychannels
        for i in range(data["realmcount"]):

            index = i + 1
            #Set the chatrelaychannels
            chatrelaychannels.append(data[f"realm{index}"]["relaychannel"])
           
            #Auto Rejoining
            if (data[f"realm{index}"]["alwaysingame"] == 'True'):
                realmidtojoin = data[f"realm{index}"]["realmid"]
                #Check if the client exists
                if index in clients:
                    #Check if the client is connected
                    if clients[index].connection.connected == True:
                        print("Already Connected!")
                    else:
                        print("Client exists but wasnt connected!")
                        clients.pop(index)
                        makebotjoin(realmidtojoin, index)
                else:
                    print("Client didnt exist.")
                    makebotjoin(realmidtojoin, index)

        print(f'Updated the chatrelay channels: {chatrelaychannels}')
    
refrestokentimer.start()
# ---------------------------------------------------------------------------------------------------------------

#Get messages to send for chat relay from discord to realm
@bot.event
async def on_message(message):

    #Check if the channel is a relay channel
    if message.channel.id in chatrelaychannels:
        if message.author.id != bot.user.id:
            index = chatrelaychannels.index(message.channel.id) + 1

            #Check if the bot is in the game
            if index in clients:
                print(message.content)
                clients[index].queue('command_request', {
                    'command': 'tellraw @a {{"rawtext":[{{"text":"§8§l[§r§9Discord§8§l]§r §b{} §7>> §r{}"}}]}}'.format(message.author.display_name, message.content),
                    'origin': { 'type': 'player', 'uuid': '', 'request_id': '', },
                    'internal': False,
                    'version': 70
                })
        



#Stuff to run when the bot starts
@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    await bot.change_presence(activity=discord.Activity(name=f"Neapolis Factions.", type=discord.ActivityType.watching))

    unbantimer.start()
    tenminutetimer.start()
    
    
bot.run(os.getenv('TOKEN'))