import slack, config, cleverbot
from mcstatus import MinecraftServer
from minecraft import minecraft_watch

chat_quiet = True

bot = slack.SlackBot(api_token=config.SLACK_API_TOKEN, debug=True)
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

@bot.match_message('!minecraft')
def minecraft_status (msg):
    server = MinecraftServer.lookup("minecraft.westsixth.net:25565")
    query = server.query()
    if not query.players.names:
         bot.say(msg.channel, "Nobody is on :-(")
         bot.say(msg.channel, "The server is running version {0} at the moment.".format("".join(query.software.version)))
    else:
        bot.say(msg.channel, "The following people are on: {0}".format(", ".join(query.players.names)))
        bot.say(msg.channel, "The server is running version {0} at the moment.".format("".join(query.software.version)))


bot.run()