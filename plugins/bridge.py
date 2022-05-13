from ircked.bot import irc_bot
from ircked.message import *

hooks = ["READY", "MESSAGE_CREATE"]

dorfl = None

disc_bot_instance = None

init = False

def run(event, ctx, bot):
    global init
    global dorfl
    global disc_bot_instance
    if event == "READY":
        disc_bot_instance = bot
        if init:
            return
        init = True
        dorfl = irc_bot(nick = disc_bot_instance.config["irc_nick"])
        dorfl.connect_register("irc.rizon.net", 7000)
        
        def magic(msg, ctx):
            if msg.command == "PING":
                message.manual("", "PONG", msg.parameters).send(ctx.socket)
            elif msg.command == "001":
                message.manual("", "JOIN", [disc_bot_instance.config["irc_channel"]]).send(ctx.socket)
            elif msg.command == "PRIVMSG" and "\x01VERSION\x01" in msg.parameters:
                message.manual(":"+msg.parameters[0], "PRIVMSG", [msg.prefix[1:].split("!")[0], ":\x01dorfl bot\x01"]).send(ctx.socket)
            if msg.command == "PRIVMSG" and ("py-ctcp" not in msg.prefix):
                pm = privmsg.parse(msg)
                disc_bot_instance.execute_webhook(disc_bot_instance.config["discord_webhook"], pm.bod, pm.fr.split("!")[0]+" (IRC)")

        dorfl.run(event_handler = magic)
    elif event == "MESSAGE_CREATE" and init == True and ctx["channel_id"] == disc_bot_instance.config["discord_channel"] and not(bool(ctx.get("webhook_id"))):
        authname = (ctx["author"]["username"] if ctx.get("member").get("nick") == None else ctx["member"]["nick"])
        dorfl.sendraw(privmsg.build(disc_bot_instance.config["irc_nick"], disc_bot_instance.config["irc_channel"], authname+" (discord): "+ctx["content"]).msg)
        for att in ctx["attachments"]:
            dorfl.sendraw(privmsg.build(disc_bot_instance.config["irc_nick"], disc_bot_instance.config["irc_channel"], authname + " uploaded a file"+" ("+att["filename"]+"): "+att["proxy_url"]).msg)
