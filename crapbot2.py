import slack, config, cleverbot, threading, ConfigParser, random, re, json, faceswap, sys
from mcstatus import MinecraftServer
from minecraft import minecraft_watch
from imgurpython import ImgurClient

chat_quiet = True
run = True

bot = slack.SlackBot(api_token=config.SLACK_API_TOKEN, debug=True)

#Configuration Variables
def load_config():
    # Load Config
    global slack_api_token, slack_channel, keyword_file, send_greetings, wolfram_app_id
    global imgur_client_id, imgur_client_secret, imgur_access_token, imgur_refresh_token
    '''Load bot options from config file'''
    config = ConfigParser.RawConfigParser()
    config.read('crapbot.cfg')
    slack_api_token = config.get('General', 'api_token')
    slack_channel = config.get('General', 'slack_channel')
    keyword_file = config.get('General', 'keyword_file')
    send_greetings = config.getboolean('General', 'greet_people')
    refrigerators_file = config.get('General', 'refrigerators_file')
    wolfram_app_id = config.get('General', 'wolfram_app_id')
    imgur_client_id = config.get('General','imgur_client_id')
    imgur_client_secret = config.get('General','imgur_client_secret')
    imgur_access_token = config.get('General','imgur_access_token')
    imgur_refresh_token = config.get('General','imgur_refresh_token')

load_config()

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
    minecraft_watch(msg, bot, stop_event)

#Create Minecraft Stop Event
s = threading.Event()
thread_count = 0

@bot.match_message('!minecraft_speakup')
def minecraft_start(msg):
    global thread_count
    if thread_count is 0:
        d = threading.Thread(name='minecraft', target=minecraft_speakup, args=(msg,s,))
        d.setDaemon(True)
        d.start()
        thread_count = 1
    else:
        bot.say(msg.channel, "Already running sir!")

@bot.match_message('!minecraft_shutup')
def minecraft_stop(msg):
    global thread_count
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
        thread_count = 0

#Imgur API

@bot.match_message('!imgur')
def imgur_search (msg):
    client = ImgurClient(imgur_client_id, imgur_client_secret)
    search = re.match('^!imgur (.*)$', msg.text, re.I)
    items = client.gallery_search(search.groups()[0], advanced=None, sort='top', window='all', page=0)
    if not items:
        bot.say(msg.channel,":buch: No results for {0}".format("".join(search.groups()[0])))
    else:
        item = random.choice(items)
        #item = items[0]
        bot.say(msg.channel,item.link)

@bot.match_message('!gif')
def imgur_gifsearch (msg):
    client = ImgurClient(imgur_client_id, imgur_client_secret)
    search = re.match('^!gif (.*)$', msg.text, re.I)
    items = client.gallery_search(search.groups()[0] + ' ext: gif AND animated: 1', advanced=None, sort='top', window='all', page=0)
    if not items:
        bot.say(msg.channel,":buch: No results for {0}".format("".join(search.groups()[0])))
    else:
        item = random.choice(items)
        #item = items[0]
        bot.say(msg.channel,item.link)

@bot.match_message('!seinfeld')
def seinfeld(msg):
    client = ImgurClient(imgur_client_id, imgur_client_secret)
    search = re.match('^!seinfeld (.*)$', msg.text, re.I)
    items = client.subreddit_gallery('seinfeldgifs', sort='top', window='week', page=0)
    if not items:
        bot.say(msg.channel, ":buch: No results for {0}".format("".join(search.groups()[0])))

    else:
        item = random.choice(items)
        # item = items[0]
        bot.say(msg.channel, item.link)

#Faceoff
def imgur_upload(image, name):
    client = ImgurClient(imgur_client_id, imgur_client_secret)
    authorization_url = client.get_auth_url('pin')
    client.set_user_auth(imgur_access_token, imgur_refresh_token)
    config = {
            'album': 'IbzLr',
            'name':  name,
            'title': name,
            'description': name
            }
    image = client.upload_from_path(image, config=config, anon=False)
    return image['link']

@bot.match_message('!faceoff')
def faceoff (msg):
    try:
        images = re.match('^!faceoff (.*) (.*)$', msg.text, re.I)
        names_file = open("names.json","r")
        names = json.load(names_file)
        names_file.close()
        print images.groups()[0]
        print images.groups()[1]
        url1 = images.groups()[0]
        url2 = images.groups()[1]
        if names.has_key(url1.lower()):
		    url1 = names[url1.lower()]
        if names.has_key(url2.lower()):
		    url2 = names[url2.lower()]
        print url1
        print url2
        faceswap.swap_face(url1, url2)
        link = imgur_upload('output.jpg', url2)
        bot.say(msg.channel,link)
    except faceswap.NoFaces:
        bot.say(msg.channel, 'No faces detected. :ignore_it:')
    except faceswap.TooManyFaces:
        bot.say(msg.channel, 'Too many faces! :ignore_it:')
    except:
        e = e = sys.exc_info()[0]
        bot.say('debug', e)

@bot.match_message('!facecheck')
def facecheck(msg):
    try:
        images = re.match('^!facecheck (.*)$', msg.text, re.I)
        names_file = open("names.json","r")
        names = json.load(names_file)
        names_file.close()
        url1 = images.groups()[0]
        if images.groups()[0]:
		    url1 = names[url1.lower()]
        faceswap.check_face(url1)
        bot.say(msg.channel, ':claudette:Look at that face!')
    except faceswap.NoFaces:
        bot.say(msg.channel, 'No faces detected. :ignore_it:')
    except faceswap.TooManyFaces:
        bot.say(msg.channel, 'Too many faces! :ignore_it:')
    except:
        e = sys.exc_info()[0]
        bot.say('debug', e)

@bot.match_message('!facelist')
def facelist(msg):
    images = re.match('^!facelist(.*)$', msg.text, re.I)
    names_file = open("names.json","r")
    names = json.load(names_file)
    names_file.close()
    url1 = images.groups()[0]
    bot.say(msg.channel, 'Commands are !faceoff <destination face> <source face>, !faceadd <name> <url>, !faceremove <name>')
    if images.groups()[0]:
        url1 = names[url1.lower()]
        bot.say(msg.chanel, url1)
    else:
        players = ''
        for key in names:
            players += key + ", "
        bot.say(msg.channel, players)

@bot.match_message('!faceadd')
def faceadd(msg):
    print "Face Add!"
    images = re.match('^!faceadd (.*) (.*)$', msg.text, re.I)
    name = images.groups()[0]
    url = images.groups()[1]

    names = {name : url}

    with open('names.json') as f:
        data = json.load(f)

    data.update(names)

    with open('names.json', 'w') as f:
        json.dump(data, f)

    f.close()

    bot.say(msg.channel, ":claudette: Face added!")

@bot.match_message('!faceremove')
def faceremove(msg):
    print "Face Remove!"
    images = re.match('^!faceremove (.*)$', msg.text, re.I)
    name = images.groups()[0]
    with open('names.json') as f:
        data = json.load(f)

    data.pop(name, None)

    with open('names.json', 'w') as f:
        json.dump(data, f)

    f.close()

    bot.say(msg.channel, ':claudette:  Face removed! Do you have a secure position?')


bot.run()