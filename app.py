import logging
from bot.bot import OSMbot

from flask import Flask, request, current_app
from bot import Osmbot
from configobj import ConfigObj

application = Flask(__name__)
application.debug = True
Osmbot(application, '')

config = ConfigObj("bot.conf")
token = config["token"]
bot = OSMbot(token)

f = open("certificate.crt", "r")
cert_data = f.read()
f.close()
application.logger.debug("webhook:%s", config['webhook'])
response = bot.setWebhook(config['webhook'], cert_data)
application.logger.debug("response:%s", response)

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
