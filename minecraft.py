import time,re
minecraft_stop = False


def watch(fn, words):
    fp = open(fn, 'r')
    while True:
        new = fp.readline()
        # Once all lines are read this just returns ''
        # until the file changes and a new line appears

        if new:
            for word in words:
                if word in new:
                    yield (word, new)
        else:
            time.sleep(0.5)
            if minecraft_stop:
                thread.exit()

def minecraft_watch(bot,msg):
    fn = '/opt/minecraft/logs/latest.log'
    #fn = '/Users/eric/Documents/latest.log'
    words = ['joined the game']
    for hit_word, hit_sentence in watch(fn, words):
        output = re.match('([^\s]+) ([^\s]+) ([^\s]+) ([^\s]+)', hit_sentence, re.I)
        bot.say(msg.channel, ':tanky:%s has joined Minecraft' % (output.group(4)))