from javascript import require, On
bedrock = require('bedrock-protocol')

import discord
from discord.ext import tasks

import commandapis as cmds

import re

async def sendmessage(thing, bot, channel):
    print(channel)
    await channel.send(thing)

async def sendembed(thing, bot, channel, ping = False):
    print(channel)
    await channel.send(embed=thing)
    if ping == True:
        await channel.send('<@614570887160791050><@370759023533883394>', embed=thing)
    
def start(client, bot, relaychannel, joinlogschannel, cmdlogschannel):
    try:
        from javascript import require, On
        bedrock = require('bedrock-protocol')


        #Make it false if disabled
        if relaychannel != False:
            relaychannelobject = bot.get_channel(relaychannel)
        if joinlogschannel != False:
            joinlogschannelobject = bot.get_channel(joinlogschannel)
        if cmdlogschannel != False:
            cmdlogschannelobject = bot.get_channel(cmdlogschannel)

        @On(client, 'error')
        def handle(_, err):
            print(f"An error occurred: {err}")

        print("joining...")
        @On(client, 'join')
        def handle(event):
            print(f"joined the game baby!")

        
        @On(client, 'text') #You can use this for logging commands
        def handle(name, packet):
            print(packet)
            #When they join and leave it gives parameters
            #Check if its a join/leave message
            if joinlogschannel != False:
                if packet['message'].startswith('§e%multiplayer.player'):
                    if packet['message'] == '§e%multiplayer.player.left.realms':
                        leaveembed = cmds.embedmake('Realm Disconnection', 'red', False, False)
                        leaveembed.add_field(
                            name = "",
                            value = f"**{packet['parameters'][0]}** has just left the realm!",
                            inline = "False"
                        )
                        bot.loop.create_task(sendembed(leaveembed, bot, joinlogschannelobject))
                    else:
                        joinembed = cmds.embedmake('Realm Connection', 'green', False, False)
                        joinembed.add_field(
                            name = "",
                            value = f"**{packet['parameters'][0]}** has just joined the realm!",
                            inline = "False"
                        )
                        if packet['parameters'][0].endswith('(2)'):
                            bot.loop.create_task(sendembed(joinembed, bot, joinlogschannelobject, ping = True))
                        else:
                            bot.loop.create_task(sendembed(joinembed, bot, joinlogschannelobject))

            #Check if chatrelay is disabled
            if relaychannel != False:
                print("Received text:", packet['message'])

                #Relay For The Chat
                if 'source_name' in packet:
                    if '@everyone' in packet['message'] or '@here' in packet['message'] or '<@' in packet['message']:
                        bot.loop.create_task(sendmessage(f"**{packet['source_name']}** just tried pinging everyone LOL", bot, relaychannelobject))
                    elif packet.get('type') == 'announcement':
                        print("sending message")
                        bot.loop.create_task(sendmessage(f"{re.sub(r'§.', '', packet['message'])}", bot, relaychannelobject))
                    else:
                        print("sending message")
                        bot.loop.create_task(sendmessage(f"**{packet['source_name']}:** {packet['message']}", bot, relaychannelobject))
                
                #Relay For RawText/Chat Ranks
                elif packet.get('type') == 'json_whisper':
                    if '@everyone' in packet['message'] or '@here' in packet['message'] or '<@' in packet['message']:
                        bot.loop.create_task(sendmessage(f"some monkey just tried pinging everyone", bot, relaychannelobject))
                    else:
                        #Make the string into normal text
                        message = str({re.sub(r'§.', '', packet['message'])})

                        pattern = r'"text":"(.*?)"'
                        message = re.search(pattern, message).group(1)


                        print("sending message")
                        #Check if its a discord message
                        if 'Discord' not in message:
                            #Check if its chat ranks or other
                            if '>>' in message:
                                #Put name in bold then send
                                message = message.replace('[', '**[', 1)
                                message = message.replace(':', ':**', 1)
                                bot.loop.create_task(sendmessage(f"{message}", bot, relaychannelobject))
                            else:
                                bot.loop.create_task(sendmessage(f"{message}", bot, relaychannelobject))
            
                #Relay For Death Messages
                elif packet.get('message') == 'death.attack.player':
                    print("sending message")
                    bot.loop.create_task(sendmessage(f"**{packet['parameters'][0]}** was slain by **{packet['parameters'][1]}**", bot, relaychannelobject))
                elif packet.get('message') == 'death.attack.player.item':
                    print("sending message")
                    bot.loop.create_task(sendmessage(f"**{packet['parameters'][0]}** was slain by **{packet['parameters'][1]}** using **{packet['parameters'][2]}**", bot, relaychannelobject))

            #Relay for commands
            if cmdlogschannel != False:
                if 'commands.' in packet.get('message'):
                    bot.loop.create_task(sendmessage(packet.get('message'), bot, cmdlogschannelobject))

    except Exception as e:
        print(f"An error occured: {e}")
        return
    




        

