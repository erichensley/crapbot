import time,re
minecraft_stop = False


# def watch(fn, words):
#     fp = open(fn, 'r')
#     while True:
#         new = fp.readline()
#         # Once all lines are read this just returns ''
#         # until the file changes and a new line appears
#
#         if new:
#             for word in words:
#                 if word in new:
#                     yield (word, new)
#         else:
#             time.sleep(0.5)
#             if minecraft_stop:
#                 thread.exit()
#
# def minecraft_watch(bot,msg):
#     #fn = '/opt/minecraft/logs/latest.log'
#     fn = '/Users/eric/Documents/latest.log'
#     words = ['joined the game']
#     for hit_word, hit_sentence in watch(fn, words):
#         output = re.match('([^\s]+) ([^\s]+) ([^\s]+) ([^\s]+)', hit_sentence, re.I)
#         bot.say(msg.channel, ':tanky:%s has joined Minecraft' % (output.group(4)))


def tail(filepath):
    '''Generator providing new lines in an open file'''
    with open(filepath) as f:
        while True:
            new = f.readline()
            if new:
                yield new
            else:
                time.sleep(0.5)
                if minecraft_stop:
                    thread.exit()


def join_match(line): pass
def left_match(line): pass
def says_match(line): pass
def died_match(line): pass
def chat_match(line): pass




def minecraft_watch(bot, msg):
    log_file = '/opt/minecraft/logs/latest.log'
    #log_file = '/Users/eric/Documents/latest.log'

    patterns = {
                'joined the game': join_match,
                'left the game':  left_match,
                'says':            says_match,
                'died':            died_match,
                '<.*>':            chat_match
              }
    for line in tail(log_file):
        for pattern in patterns:
            if re.search(pattern, line):
                bot.say(msg.channel, line)
