# -*- coding: utf-8 -*-
from flask import Flask
from flask import request, abort,current_app
import re
import nominatim
import sched, time
from osmapi import OsmApi

import urllib
from configobj import ConfigObj
from typeemoji import typeemoji
from maptools import download,genBBOX
import gettext
from flask import render_template, current_app, Blueprint



import user as u
avaible_languages = ['Catalan', 'English', 'Spanish', 'Swedish']

application = Flask(__name__)
application.debug = True
config = ConfigObj("bot.conf")
token = config["token"]


osmbot = Blueprint(
    'osmbot', __name__,
    template_folder='templates',
    static_folder='static'
)


@osmbot.route("/hook/<string:token>", methods=["POST"])
def attend_webhook(token):
    current_app.logger.debug("token:%s", token)
    if token == config['token']:
        current_app.logger.debug("data:%s",request.json['message'])
        return "OK"
    else:
        return "NOT ALLOWED"

if __name__ == "__main__":

    application.run(host='0.0.0.0')
