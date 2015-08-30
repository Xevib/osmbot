import logging
from . import Osmbot

from flask import Flask, request
from bot import OSMbot
from configobj import ConfigObj

application = Flask(__name__)
application.debug = True
OSMbot(application, '')

config = ConfigObj("bot.conf")
token = config["token"]
bot = OSMbot(token)

f = open("certificate.crt", "r")
cert_data = f.read()
f.close()
bot.setWebhook(config['webhook'], cert_data)

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
