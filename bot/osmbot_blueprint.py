# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import Flask
from flask import request, current_app, Blueprint
import pynominatim
from osmapi import OsmApi
from configobj import ConfigObj
import gettext
import bot.user as u
from bot.osmbot import OsmBot
from telegram import Bot as TBot
from telegram import error
import sys
from pony.flask import Pony
from pony.orm import Database, Required, Optional, db_session
from datetime import datetime

application = Flask(__name__)
config = ConfigObj('bot.conf')
application.config.update(dict(
    DEBUG = False,
    PONY = {
        "provider": "postgres",
        "host": config.get("host", ""),
        "user": config.get("user", ""),
        "password": config.get("password", ""),
        "dbname":config.get("database", "")
    }))


db = Database()
db.bind(**application.config['PONY'])

from bot.models import Stats
db.generate_mapping(create_tables=True)



Pony(application)

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
@db_session
def attend_webhook(token):    
    user = u.User(config['host'], config['database'], config['user'], config['password'])

    current_app.logger.debug('token:%s', token)
    osmbot.set_group(False)
    
    if token == config['token']:
        try:
            query = request.json
            
            if 'edited_channel_post' in query:
                return 'OK'
            if 'channel_post' in query:
                return 'OK'
            if 'edited_message' in query:
                return 'OK'
            message_type = ''
            if 'message' in query:
                message_dict = query['message']
                message_type = 'query'

                if 'from' in message_dict and 'id' in message_dict['from']:
                    app_language = query["message"]["from"].get("language_code",None)
                    osmbot.set_group(query['message']['chat']['type'] == u'group')
                    if osmbot.get_group():
                        identifier = message_dict['chat']['id']
                        if "text" in message_dict:
                            command = message_dict["text"].split()[0]
                        else:
                            command = None
                    else:
                        identifier = message_dict['from']['id']
                        if "text" in message_dict:
                            command = message_dict["text"].split()[0]
                        else:
                            command = None
                    user_config = user.get_user(identifier, group=osmbot.get_group())
                    user_id = message_dict['from']['id']
                    if app_language and user_config.get("lang") and command:
                        Stats(date= datetime.now() , user_language=app_language, configured_language=user_config.get("lang"), command=command)
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

                if osmbot.get_group() and (not user_config['onlymentions'] and user_config['onlymentions'] is not None)and '@osmbot' not in message.lower():
                    if message not in ['Yes', 'No', 'Language', 'Answer only when mention?'] and message not in osmbot.get_languages().keys():
                        return 'OK'
                else:
                    message = message.replace('@osmbot', '')
                    message = message.replace('@OSMbot', '')
            if not 'callback_query' in query:
                message = osmbot.clean_message(message)
                osmbot.load_language(user_config['lang'])
                osmbot.answer_message(message, query, chat_id, user_id, user_config, user, message_type)
            else:
                osmbot.answer_callback(query)
            return 'OK'
        except error.Unauthorized:
            return 'OK'
        except Exception as e:
            if sys.version_info.major ==2:
                if e.message == 'Unauthorized':
                    return 'OK'
            else:
                if str(e) == 'Unauthorized':
                    return 'OK'

            print(str(e))
            import traceback
            traceback.print_exc()
            current_app.sentry.captureException()
            try:
                osmbot.load_language(user_config['lang'])
                text = osmbot._get_template('error_message.md').render()
                telegram_api.sendMessage(chat_id, text)
            except Exception:
                pass
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
