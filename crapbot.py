import ConfigParser, json, re, urllib2
import xml.etree.ElementTree as ET
import random
import sys
from random import randint
from mcstatus import MinecraftServer
from imgurpython import ImgurClient
import cleverbot
#import markov
import faceswap
from SlackBot import SlackBot
from minecraft import minecraft_watch
import thread

slack_channel_id = None
keyword_mappings = {}
wolfram_app_id = None
quiet_mode = False
chat_quiet = True
minecraft_stop = False

def load_config():
    '''Load bot options from config file'''
    global slack_api_token, slack_channel, keyword_file, send_greetings, wolfram_app_id
    global imgur_client_id,imgur_client_secret,imgur_access_token,imgur_refresh_token
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

def load_keywords():
    '''Load keyword matching patterns from JSON file'''
    global keyword_mappings
    f = open(keyword_file, 'r')
    keyword_mappings = json.loads(f.read())
    f.close()

def on_open(bot):
    '''Finds the ID for the preferred channel and then greets everyone'''
    global slack_channel_id
    for channel in bot.channels:
        if channel.name == slack_channel:
            slack_channel_id = channel.id
            break
    #bot.say(slack_channel_id, 'HELLO CLASS!!!')

def listen_for_keywords(bot, msg):
    '''Event handler that watches chat messages for certain keywords (stored as
    regular expressions in a JSON file, and then responds according to a mapping
    of keyword expressions to responses'''
    global keyword_mappings, quiet_mode

    if quiet_mode:
        return

    if msg.user != bot.user_id and msg.channel == slack_channel_id:
        if keyword_mappings == {}:
            load_keywords()
            
        for pattern in keyword_mappings:
            if re.search(pattern, msg.text, re.I):
                bot.say(slack_channel_id, keyword_mappings[pattern])
                break

def reload_command(bot, msg):
    load_config()
    load_keywords()
    bot.say(msg.channel, 'OKAY!!!')

def say_command(bot, msg):
    match = re.match('^!say (.*)$', msg.text, re.I)
    bot.say(slack_channel_id, match.groups()[0])
    
def yell_command(bot, msg):
    match = re.match('^!yell (.*)$', msg.text, re.I)
    bot.say(slack_channel_id, match.groups()[0].upper())

def refrigerators_command(bot, msg):
    f = open('refrigerators.txt', 'r')
    lyrics = f.readlines()
    verses = []
    verse = ''
    for line in lyrics:
        if line != '\n':
            verse += line
        else:
            verses.append(verse)
            verse = ''
    verses.append(verse)

    verse_no = randint(0, len(verses) - 1)
    for line in verses[verse_no].split('\n'):
        if line:
            bot.say(msg.channel, '_{}_'.format(line))
    
def totinos_command(bot, msg):
    bot.say(msg.channel, 'https://www.youtube.com/watch?v=NAalGQ5LSpA')

def kris_command(bot, msg):
    bot.say(msg.channel, 'https://lh3.googleusercontent.com/o4shSu16vzXDbYsbW87zMRao4Oa5-Y5ySxgjtlZG0Dk=w640-h960-no')

def eric_command(bot, msg):
    bot.say(msg.channel, 'https://westsixth.slack.com/files/eric/F06NMPQ8Z/slack_for_ios_upload.jpg')

def grumble_command(bot, msg):
    bot.say(msg.channel, 'http://www.secrettoeverybody.com/images/grumble.png')

def clickbait_command(bot, msg):
    subjects = ['They', 'He', 'She', 'Scientists', 'Researchers', 'The government', 'Advertisers', 'Politicians']
    verbs = ['saw', 'ate', 'produced', 'created', 'destroyed', 'painted', 'taught', 'bought']
    adjectives = ['short', 'tall', 'online', 'intelligent', 'hungry', 'thirsty', 'obese']
    objects = ['cats', 'dogs', 'turtles', 'trees', 'buildings', 'people', 'actors', 'parents', 'children', 'countries']
    extras = ['in one day', 'on the Internet', 'in a foreign country', 'on television']
    subjects2 = ['What happened next', 'The result', 'Their conclusion', 'The outcome', 'What I learned']
    results = ['will blow your mind', 'made my mouth drop', 'was incredible', 'will change your life', 'was shocking', 'is terrifying']

    bait = '%s %s %d %s %s %s. %s %s.' % (subjects[randint(0, len(subjects) - 1)],
                                          verbs[randint(0, len(verbs) - 1)],
                                          randint(1, 100),
                                          adjectives[randint(0, len(adjectives) - 1)],
                                          objects[randint(0, len(objects) - 1)],
                                          extras[randint(0, len(extras) - 1)],
                                          subjects2[randint(0, len(subjects2) - 1)],
                                          results[randint(0, len(results) - 1)])
    bot.say(msg.channel, '_%s_' % bait)

def lookup_command(bot, msg):
    def wolfram_lookup(query):
        '''Uses Wolfram Alpha REST API'''
        global wolfram_app_id

        api_uri = 'http://api.wolframalpha.com/v2/query?'
        request_uri = api_uri + 'input=' + urllib2.quote(query) + '&appid=' + wolfram_app_id
        xml = urllib2.urlopen(request_uri).read()

        blacklisted_pods = ['Input', 'Input interpretation']

        root = ET.fromstring(xml)

        for child in root:
            if child.tag == 'pod':
                if child.attrib['title'] not in blacklisted_pods:
                    for node in child.iter('plaintext'):
                        return node.text
        else:
            return 'Unknown'

    match = re.match('^!lookup (.*)$', msg.text, re.I)
    result = wolfram_lookup(match.groups()[0])
    bot.say(msg.channel, result)

def chatenabled(bot, msg):
    global chat_quiet
    chat_quiet = False
    bot.say(msg.channel, 'Yo yo yo Crapbot in da house!')

def chatdisabled(bot, msg):
    global chat_quiet
    chat_quiet = True
    bot.say(msg.channel, 'Fiiiine. I will shut up.')


def speakup_command(bot, msg):
    global quiet_mode
    quiet_mode = False


def greet_people(bot, msg):
    '''Event handler that sends a greeting to users when they return to the
    chat'''
    if not send_greetings:
        return
    
    if msg.user == bot.user_id:
        return
    
    for user in bot.users:
        if user.id == msg.user:
            break
        
    if msg.presence == 'active':
        if user.presence != msg.presence:
            user.presence = 'active'
            bot.say(slack_channel_id, 'HELLO %s!!!' % user.username)
    else:
        user.presence = msg.presence

def chatbot(bot, msg):
    global chat_quiet

    if chat_quiet:
        return

    cleverbot_client = cleverbot.Cleverbot()

    if msg.user == bot.user_id:
        return

    for user in bot.users:
        if user.id == msg.user:
            break

    if msg.channel == slack_channel_id:
        bot.say(slack_channel_id, cleverbot_client.ask(msg.text))

def minecraft_status (bot, msg):
    server = MinecraftServer.lookup("minecraft.westsixth.net:25565")
    query = server.query()
    if not query.players.names:
         bot.say(msg.channel, "Nobody is on :-(")
         bot.say(msg.channel, "The server is running version {0} at the moment.".format("".join(query.software.version)))
    else:
        bot.say(msg.channel, "The following people are on: {0}".format(", ".join(query.players.names)))
        bot.say(msg.channel, "The server is running version {0} at the moment.".format("".join(query.software.version)))

def imgur_search (bot, msg):
    client = ImgurClient(imgur_client_id, imgur_client_secret)
    search = re.match('^!imgur (.*)$', msg.text, re.I)
    items = client.gallery_search(search.groups()[0], advanced=None, sort='top', window='all', page=0)
    #item = random.choice(items)
    if not items:
        bot.say(msg.channel,":buch: No results for {0}".format("".join(search.groups()[0])))
    else:
        item = items[0]
        bot.say(msg.channel,item.link)

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


def faceoff (bot, msg):
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

def facecheck(bot,msg):
    try:
        images = re.match('^!facecheck (.*)$', msg.text, re.I)
        names_file = open("names.json","r")
        names = json.load(names_file)
        names_file.close()
        url1 = images.groups()[0]
        if names.has_key(url1.lower()):
		    url1 = names[url1.lower()]
        faceswap.check_face(url1)
        bot.say(msg.channel, ':claudette:Look at that face!')
    except faceswap.NoFaces:
        bot.say(msg.channel, 'No faces detected. :ignore_it:')
    except:
        e = sys.exc_info()[0]

def facelist(bot,msg):
    with open('names.json') as f:
        data = json.load(f)
    bot.say(msg.channel, 'Commands are !faceoff <destination face> <source face>, !faceadd <name> <url>, !faceremove <name>')

    players = ''

    for key in data:
        players += data[key] + ", "

    bot.say(msg.channel, players)



def faceadd(bot,msg):
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

    bot.say(msg.channel, ":claudette: Face added! I have breast cancer!")

def faceremove(bot,msg):
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

def minecraft_speakup(bot,msg):
    thread.start_new(minecraft_watch,(bot,msg))
    bot.say(msg.channel, ':tanky: Anyone want to play Minecraft?')

def minecraft_shutup(bot,msg):
    minecraft_stop = True
    bot.say(msg.channel, ':tanky:  Awww come on guys')

load_config()

buch = SlackBot(slack_api_token)
buch.show_typing = True

buch.add_event_listener('open', on_open)
buch.add_event_listener('message', listen_for_keywords)
buch.add_event_listener('presence_change', greet_people)
buch.add_event_listener('message', chatbot)

buch.add_command('reload', reload_command)
buch.add_command('say', say_command)
buch.add_command('yell', yell_command)
#buch.add_command('refrigerators', refrigerators_command)
#buch.add_command('totinos', totinos_command)
#buch.add_command('kris', kris_command)
#buch.add_command('grumble', grumble_command)
#buch.add_command('clickbait', clickbait_command)
#buch.add_command('lookup', lookup_command)
#buch.add_command('shutup', shutup_command)
#buch.add_command('speakup', speakup_command)
#buch.add_command('markov', markov_command)
#buch.add_command('eric', eric_command)

#Crapbot Specific Commands #
buch.add_command('chatenabled', chatenabled)
buch.add_command('chatdisabled', chatdisabled)
buch.add_command('minecraft', minecraft_status)
buch.add_command('imgur', imgur_search)
buch.add_command('faceoff', faceoff)
buch.add_command('facecheck', facecheck)
buch.add_command('faceadd', faceadd)
buch.add_command('faceremove', faceremove)
buch.add_command('facelist', facelist)
buch.add_command('minecraft_speakup', minecraft_speakup)
buch.add_command('minecraft_shutup', minecraft_shutup)

#thread.start_new(buch.run, ())
buch.run()
