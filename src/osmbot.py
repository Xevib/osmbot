# -*- coding: utf-8 -*-
from flask import Flask
from flask import request, abort,current_app
import re
import nominatim
import sched, time
from osmapi import OsmApi
from bot import OSMbot
import urllib
from configobj import ConfigObj
from typeemoji import typeemoji
from maptools import download,genBBOX
import gettext

import user as u
avaible_languages = ['Catalan', 'English', 'Spanish', 'Swedish']

application = Flask(__name__)
application.debug = True
config = ConfigObj("bot.conf")

@application.route("/hook/<string:token>",methods=["POST"])
def attend_webhook(token):
    current_app.logger.debug("token:%s",token)
    if token == config['token']:
        return "OK"
    else:
        return "NOT ALLOWED"

if __name__ == "__main__":
    application.run(host='0.0.0.0')