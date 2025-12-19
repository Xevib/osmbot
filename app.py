import logging

from flask import Flask, request, current_app
from bot import Osmbot
from configobj import ConfigObj
import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import telegram

application = Flask(__name__)
application.debug = True
Osmbot(application, '')

config = ConfigObj('bot.conf')
token = config['token']
telegram_api = telegram.Bot(config['token'])
if 'sentry_dsn' in config:
    sentry_sdk.init(
        dsn=config['sentry_dsn'],
        integrations=[FlaskIntegration()],
    )
    application.config['sentry_dsn'] = config['sentry_dsn']

webhook = os.path.join(config['webhook'], config['token'])
application.logger.debug('webhook:%s', config['webhook'])
result = telegram_api.setWebhook(webhook)
if result:
    application.logger.debug('Webhook set')


if __name__ == '__main__':
    application.run(host='0.0.0.0', debug=True)
