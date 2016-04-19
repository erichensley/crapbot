import time, re, subprocess, select, sys, threading
from pygtail import Pygtail

def tail(filepath):
    f = subprocess.Popen(['tail', '-F', filepath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = select.poll()
    p.register(f.stdout)

    while True:
        if p.poll(1):
            yield f.stdout.readline()
        else:
            time.sleep(1)


def join_match(line): pass


def left_match(line): pass


def says_match(line): pass


def died_match(line): pass


def died2_match(line): pass


def chat_match(line): pass


def minecraft_watch(msg, bot, minecraft_stop):
    try:
        # log_file = '/opt/minecraft/logs/latest.log'
        bot.say(msg.channel, "Starting server log watch on minecraft.westsixth.net...")
        log_file = '/Users/eric/Documents/latest.log'
        patterns = {
            'joined the game': join_match,
            'left the game': left_match,
            'says': says_match,
            'died': died_match,
            '!s': chat_match,
            'was': died2_match
        }
        while not minecraft_stop.isSet():
            unread = Pygtail(log_file)
            for line in unread:
                for pattern in patterns:
                    if re.search(pattern, line):
                        bot.say(msg.channel, line)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
    finally:
        minecraft_stop.clear()
