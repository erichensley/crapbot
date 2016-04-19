import slack, config, cleverbot, threading
from mcstatus import MinecraftServer
from minecraft import minecraft_watch

chat_quiet = True
run = True

bot = slack.SlackBot(api_token=config.SLACK_API_TOKEN, debug=True)

# Cleverbot Chat
cleverbot_client = cleverbot.Cleverbot()

@bot.match_message('!chatenabled')
def chatenabled(msg):
    global chat_quiet
    chat_quiet = False
    bot.say(msg.channel, 'Yo yo yo Crapbot in da house!')

@bot.on_message
def chatbot(msg):
    global chat_quiet

    if chat_quiet:
        return

    if msg.user == bot.user_id:
        return

    for user in bot.users:
        if user.id == msg.user:
            break

    bot.say(msg.channel, cleverbot_client.ask(msg.text))

@bot.match_message('!chatdisabled')
def chatdisabled(msg):
    global chat_quiet
    chat_quiet = True
    bot.say(msg.channel, 'Fiiiine. I will shut up.')

#Minecraft Status

@bot.match_message('!minecraft')
def minecraft_status (msg):
    try:
        server = MinecraftServer.lookup("minecraft.westsixth.net:25565")
        query = server.query()
        if not query.players.names:
             bot.say(msg.channel, "Nobody is on :-(")
             bot.say(msg.channel, "The server is running version {0} at the moment.".format("".join(query.software.version)))
        else:
            bot.say(msg.channel, "The following people are on: {0}".format(", ".join(query.players.names)))
            bot.say(msg.channel, "The server is running version {0} at the moment.".format("".join(query.software.version)))

    except:
        bot.say(msg.channel, "The server timed out. Do you have allow query enabled?")



def minecraft_speakup(msg, stop_event):
    try:
        minecraft_watch(msg, bot, stop_event)
    except:
        bot.say(msg.channel, "There was an error reading the server log :ignore_it:")

#Create Minecraft Stop Event
s = threading.Event()
running = False

@bot.match_message('!minecraft_speakup')
def minecraft_start(msg):
    if running is False:
        d = threading.Thread(name='minecraft', target=minecraft_speakup, args=(msg,s,))
        d.setDaemon(True)
        d.start()
    else:
        bot.say(msg.channel, "Already running sir!")

@bot.match_message('!minecraft_shutup')
def minecraft_stop(msg):
    try:
        bot.say(msg.channel, "Stopping log watch...")
        d = threading.Thread(name='minecraft', target=minecraft_speakup, args=(msg, s,))
        s.set()
        if not d.isAlive():
            bot.say(msg.channel, "Logging stopped :enjoy_it:")
    except:
        bot.say(msg.channel, "There was an error stopping. :ignore_it:")
    finally:
        s.clear()

#TODO: Add Minecraft Log Watch

#Imgur API

#TODO: Make random imgur from subreddit function


bot.run()