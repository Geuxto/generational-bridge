from ircked.bot import irc_bot
from ircked.message import *

hooks = ["READY", "MESSAGE_CREATE"]

# replace all this stuff and it should maybe probablyt just werk (tm)
_discord_webhook = "https://discord.com/api/webhooks/937542041678798969/U6_y4tw-Kjrjz4ivtiVqw4Sk8E4pFR51VtFD0nd8r_2jrwLtzFInqpfQBJJIkyoYdynk"
_discord_channel = "810037417871933521"
_irc_channel = "#station"
_irc_nick = "s00bridge"

dorfl = None

disc_bot_instance = None

init = False

def run(event, ctx, bot):
    global init
    global dorfl
    if event == "READY":
        disc_bot_instance = bot
        if init:
            return
        init = True
        dorfl = irc_bot(nick = _irc_nick)
        dorfl.connect_register("irc.rizon.net", 7000)
        
        def magic(msg, ctx):
            if msg.command == "PING":
                message.manual("", "PONG", msg.parameters).send(ctx.socket)
            elif msg.command == "001":
                message.manual("", "JOIN", [_irc_channel]).send(ctx.socket)
            elif msg.command == "PRIVMSG" and "\x01VERSION\x01" in msg.parameters:
                message.manual(":"+msg.parameters[0], "PRIVMSG", [msg.prefix[1:].split("!")[0], ":\x01dorfl bot\x01"]).send(ctx.socket)
            if msg.command == "PRIVMSG" and ("py-ctcp" not in msg.prefix):
                pm = privmsg.parse(msg)
                bot.execute_webhook(_discord_webhook, pm.bod, pm.fr.split("!")[0]+" (IRC)")

        dorfl.run(event_handler = magic)
    elif event == "MESSAGE_CREATE" and init == True and ctx["channel_id"] == _discord_channel and not(bool(ctx.get("webhook_id"))):
        dorfl.sendraw(privmsg.build(_irc_nick, _irc_channel, (ctx["author"]["username"] if ctx.get("member").get("nick") == None else ctx["member"]["nick"])+" (discord): "+ctx["content"]).msg)
    