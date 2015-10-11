import logging
from bot.bot import OSMbot

from flask import Flask, request, current_app
from bot import Osmbot
from configobj import ConfigObj
import os
from raven.contrib.flask import Sentry

application = Flask(__name__)
application.debug = True
Osmbot(application, '')

config = ConfigObj('bot.conf')
token = config['token']
bot = OSMbot(token)

if 'sentry_dsn' in config:
    application.config['sentry_dsn'] = config['sentry_dsn']
    sentry = Sentry(application,dsn=config['sentry_dsn'])
    sentry.captureMessage('OSMBot started', level=logging.INFO)

f = open('nginx.crt', 'r')
cert_data = f.read()
f.close()
webhook = os.path.join(config['webhook'], config['token'])
application.logger.debug('webhook:%s', config['webhook'])
response = bot.setWebhook(webhook, cert_data)
application.logger.debug('response:%s', response)


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
