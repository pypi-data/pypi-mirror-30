import re


def nick_replace(nick):
    return nick[:-2] + "\u200B" + nick[-2:]


def msg_replace(nick, message):
    if not nick:
        return message
    escaped_nick = re.escape(nick)
    return re.sub('(' + escaped_nick[:-2] + ')(' + escaped_nick[-2:] + ')', r'\1' + "\u200B" + r'\2',
                  message, flags=re.I)
