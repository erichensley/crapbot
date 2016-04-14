import time,re
minecraft_stop = False

#Eric Note
#Look at this stackexchange article
#https://stackoverflow.com/questions/12523044/how-can-i-tail-a-log-file-in-python

def tail(filepath):
    '''Generator providing new lines in an open file'''
    with open(filepath) as f:
        while True:
            new = f.readline()
            if new:
                yield new
            else:
                time.sleep(0.5)


def join_match(line): pass
def left_match(line): pass
def says_match(line): pass
def died_match(line): pass
def died2_match(line): pass
def chat_match(line): pass

def minecraft_watch(msg, bot):
    #log_file = '/opt/minecraft/logs/latest.log'
    log_file = '/Users/eric/Documents/latest.log'

    patterns = {
                'joined the game': join_match,
                'left the game':  left_match,
                'says':            says_match,
                'died':            died_match,
                '!s':              chat_match,
                'was':             died2_match
              }
    for line in tail(log_file):
        for pattern in patterns:
            if re.search(pattern, line):
                bot.say(msg.channel, line)
