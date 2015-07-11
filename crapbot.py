import ConfigParser, json, re, urllib2
import xml.etree.ElementTree as ET
import random
from random import randint
from mcstatus import MinecraftServer
from imgurpython import ImgurClient

import markov
from SlackBot import SlackBot
import cleverbot



slack_channel_id = None
keyword_mappings = {}
wolfram_app_id = None
quiet_mode = False
chat_quiet = True

def load_config():
    '''Load bot options from config file'''
    global slack_api_token, slack_channel, keyword_file, send_greetings, wolfram_app_id, imgur_client_id,imgur_client_secret
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

def build_markov_vocab(bot, msg):
    if msg.user != bot.user_id and msg.channel == slack_channel_id:
        markov.process_text(msg.text)

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

def markov_command(bot, msg):
    bot.say(msg.channel, markov.markov_chain().upper() + '!!!')

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
    items = client.gallery_search(search.groups()[0], advanced=None, sort='viral', window='all', page=0)
    item = random.choice(items)
    bot.say(msg.channel,item.link)


load_config()

buch = SlackBot(slack_api_token)
buch.show_typing = True

buch.add_event_listener('open', on_open)
buch.add_event_listener('message', listen_for_keywords)
buch.add_event_listener('message', build_markov_vocab)
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
buch.add_command('markov', markov_command)
#buch.add_command('eric', eric_command)

#Crapbot Specific Commands #
buch.add_command('chatenabled', chatenabled)
buch.add_command('chatdisabled', chatdisabled)
buch.add_command('minecraft', minecraft_status)
buch.add_command('imgur', imgur_search)

buch.run()
