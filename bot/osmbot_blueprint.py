# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask import Flask
from flask import request, current_app, Blueprint
import pynominatim
from osmapi import OsmApi
from configobj import ConfigObj
import gettext
import bot.user as u
from bot.osmbot import OsmBot
from telegram import Bot as TBot

application = Flask(__name__)
application.debug = True
config = ConfigObj('bot.conf')

if config:
    user = u.User(config.get('host', ''), config.get('database', ''), config.get('user', ''), config.get('password', ''))
    osmbot = OsmBot(config)
    telegram_api = TBot(config['token'])

api = OsmApi()
nom = pynominatim.Nominatim()

osmbot_blueprint = Blueprint(
    'osmbot', __name__,
    template_folder='templates',
    static_folder='static'
)


@osmbot_blueprint.route('/osmbot/hook/<string:token>', methods=['POST'])
def attend_webhook(token):
    user = u.User(config['host'], config['database'], config['user'], config['password'])
    current_app.logger.debug('token:%s', token)
    if token == config['token']:
        try:
            query = request.json
            if 'edited_message' in query:
                return 'OK'
            is_group = False
            message_type = ''
            if 'message' in query:
                message_dict = query['message']
                message_type = 'query'

                if 'from' in message_dict and 'id' in message_dict['from']:
                    is_group = query['message']['chat']['type'] == u'group'
                    if is_group:
                        identifier = message_dict['chat']['id']
                    else:
                        identifier = message_dict['from']['id']
                    user_config = user.get_user(identifier, group=is_group)
                    user_id = message_dict['from']['id']
            elif 'inline_query' in query:
                message_type = 'inline'
                user_id = query['inline_query']['from']['id']
                identifier = query['inline_query']['from']['id']
                user_config = user.get_user(identifier, group=False)
                message = query['inline_query']['query']
                chat_id = 0
            else:
                user_config = user.get_defaultconfig()
                user_id = 0
            if 'message' in query:
                if 'text' in query['message']:
                    message = query['message']['text']
                else:
                    message = ''
                chat_id = query['message']['chat']['id']

                if is_group and (not user_config['onlymentions'] and user_config['onlymentions'] is not None)and '@osmbot' not in message.lower():
                    if message not in ['Yes', 'No', 'Language', 'Answer only when mention?'] and message not in osmbot.get_languages().keys():
                        return 'OK'
                else:
                    message = message.replace('@osmbot', '')
                    message = message.replace('@OSMbot', '')

            message = osmbot.clean_message(message)
            osmbot.load_language(user_config['lang'])
            osmbot.answer_message(message, query, chat_id, user_id, user_config, is_group, user, message_type)
        except Exception as e:
            print(str(e))
            import traceback
            traceback.print_exc()
            current_app.sentry.captureException()
            osmbot.load_language(user_config['lang'])
            text = osmbot._get_template('error_message.md').render()
            telegram_api.sendMessage(chat_id, text)
        return 'OK'
    else:
        return 'NOT ALLOWED'

if __name__ == '__main__':
    application.run(host='0.0.0.0')

gettext.gettext('OpenStreetMap bot finds any location in world from the Nominatim OSM database and can send links and maps from OSM')
gettext.gettext('OpenStreetMap bot finds any location in the world from the Nominatim OSM database')
gettext.gettext('The bot can send links and maps (jpg, png or pdf) from OSM')
gettext.gettext('Data for all the world (cities and towns, shops -with phone number, email...-, Wikipedia links, etc)')
gettext.gettext('OSMbot is multilingual and speaks *your language here*')
