import logging

from flask import Flask, request, current_app
from bot import Osmbot
from configobj import ConfigObj
import os
from raven.contrib.flask import Sentry
import telegram

application = Flask(__name__)
application.debug = True
Osmbot(application, '')

config = ConfigObj('bot.conf')
token = config['token']
telegram_api = telegram.Bot(config['token'])
if 'sentry_dsn' in config:
    application.config['sentry_dsn'] = config['sentry_dsn']
    sentry = Sentry(application, dsn=config['sentry_dsn'])
    sentry.captureMessage('OSMBot started', level=logging.INFO)
    application.sentry = sentry

f = open('nginx.crt', 'r')

webhook = os.path.join(config['webhook'], config['token'])
application.logger.debug('webhook:%s', config['webhook'])
result = telegram_api.setWebhook(webhook, f)
if result:
    application.logger.debug('Webhook set')


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
