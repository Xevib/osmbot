# -*- coding: UTF-8 -*-
from __future__ import absolute_import

import os
from jinja2 import Environment
import urllib
import math
import re
import gettext
import pynominatim
import overpass
import telegram
from uuid import uuid4
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, ReplyKeyboardMarkup, ReplyKeyboardHide
from io import StringIO

# local imports
from bot.user import User
from bot.typeemoji import typeemoji
from bot.maptools import download, genBBOX, getScale
from bot.utils import getData
from bot.overpass_query import type_query
from bot.emojiflag import emojiflag
from bot.error import OSMError


def url_escape(s):
    """
    Used to escape URL in template

    :param s: original URL in data
    :return: Well fomrated URL
    """
    return s.replace(' ', '%20').replace(')', '\\)')


class OsmBot(object):
    # dict with all available languages
    # TODO(edgar): load this from a local config file.
    avaible_languages = {
        'Catalan': 'ca',
        'English': 'en',
        'Spanish': 'es',
        'Swedish': 'sv',
        'Asturian': 'ast',
        'Galician': 'gl',
        'French': 'fr',
        'Italian': 'it',
        'Basque': 'eu',
        'Polish': 'pl',
        'German': 'de',
        'Dutch': 'nl',
        'Czech': 'cs',
        'Persian': 'fa',
        'Japanese': 'ja',
        'Ukrainian': 'uk',
        'Chinese (Taiwan)': 'zh_TW',
        'Vietnamese': 'vi',
        'Russian': 'ru',
        'Slovak': 'sk',
        'Chinese (Hong Kong)': 'zh_HK',
        'Hungarian': 'hu',
        'Catalan (Valencian)': 'ca@valencia',
        'Chinese (China)': 'zh_CN'
    }

    """
        Class that represents the OsmBot
    """
    def __init__(self, config, auto_init=True):
        """
        Class constructor

        :param config: Dictionary with the configuration variables
        (token,host,database,user,password)
        :param auto_init: Enable/Disable automatic init_config
        """
        # private attributes
        self.rtl_languages = None
        self.user = None
        self.jinja_env = None
        self.language = None
        self.telegram_api = None
        self.re_map = re.compile(" -?\d+(\.\d*)?,-?\d+(\.\d*)?,-?\d+(\.\d*)?,-?\d+(\.\d*)? ?(png|jpeg|pdf)? ?\d{0,2}")

        # configure osmbot
        if auto_init:
            self.init_config(config)

    def init_config(self, config):
        """
        Function that loads the configuration file.

        :param config: the configuration file
        :return: None
        """

        # TOOD(xevi): why Persian here?
        self.rtl_languages = ['fa']

        # setup the database info
        from configobj import ConfigObj
        if config and isinstance(config, ConfigObj):
            self.user = User(
                config.get('host', ''), config.get('database', ''),
                config.get('user', ''), config.get('password', ''))
        else:
            raise OSMError('No config file: ' \
                    'Please provide a ConfigObj object instance.')

        # setup the jinja environment and default language
        # TODO(xevi): Should we set a default language?
        self.jinja_env = Environment(extensions=['jinja2.ext.i18n'])
        self.jinja_env.filters['url_escape'] = url_escape
        self.language = None

        # setup the telegram API. Before check token existence
        token = config.get('token', '')
        if token:
            self.telegram_api = telegram.Bot(token)
        else:
            raise OSMError('No token in config file: ' \
                    'Please check that token is in the config file.')

    def load_language(self, language):
        """
        Function to load the language of the answer

        :param language: code of the language
        :return: None
        """
        self.language = language
        lang = gettext.translation('messages',
                                   localedir='./bot/locales/',
                                   languages=[language, 'en'])
        lang.install()
        self.jinja_env.install_gettext_translations(
                gettext.translation('messages',
                                    localedir='./bot/locales/',
                                    languages=[language, 'en']))

    def get_is_rtl(self):
        """
        Returns if the actual language is RTL

        :return: Boolean to indicate if the language is RTL
        """
        return self.language in self.rtl_languages

    # TODO(xevi): This type of getters are not good practices in Python.
    # since all 'private' variables are not reallly prvate. If we want
    # to use in that way we should use decorators.
    def get_language(self):
        """
        Retunrs the actual language code

        :return: str Language code
        """
        return self.language

    # TODO(xevi): same as above
    def get_languages(self):
        """
        Returns the avaible languages

        :return: Dict with the name of the language as a key and code as a value
        """
        return self.avaible_languages

    def get_rtl_languages(self):
        """
        Returns the list of RTL langauges

        :return: list of the code of RTL languages
        """
        return self.rtl_languages

    def _get_template(self, template_name):
        """
        Returns the text of a template

        :param template_name: The template name as a str
        :return: str with the text of the template
        """
        url = os.path.join('bot/templates', template_name)
        with open(url) as f:
            template_text = f.read()
        return self.jinja_env.from_string(template_text)

    def set_only_mention(self, message, user_id, chat_id, user, group):
        """
        Manages the set only mention requests

        :param message: Str with the message (Yes or No)
        :param user_id: User id
        :param chat_id: Chat ud
        :param user: Dict with user configuration
        :param group: Boolean to indicate if is a group
        :return: None
        """
        onlymentions = message == 'Yes'
        if group:
            user.set_field(chat_id, 'onlymentions', onlymentions, group=group)
            user.set_field(chat_id, 'mode', 'normal', group=group)
        else:
            user.set_field(user_id, 'onlymentions', onlymentions, group=group)
            user.set_field(user_id, 'mode', 'normal', group=group)
        if not onlymentions:
            text = self._get_template('only_mention.md').render()
            self.telegram_api.sendMessage(
                chat_id,
                text,
                'Markdown',
                reply_markup=ReplyKeyboardHide())
        else:
            template = self._get_template('answer_always.md')
            text = template.render(is_rtl=self.get_is_rtl())
            self.telegram_api.sendMessage(
                chat_id,
                text,
                'Markdown',
                reply_markup=ReplyKeyboardHide())
        return []

    def set_language_command(self, message, user_id, chat_id, u, group=False):
        """
        Answers the language command

        :param message: Message
        :param user_id: User identifier
        :param chat_id: Chat identifier
        :param u: User object
        :param group: Boolean to indicate if its a group
        :return: None
        """
        if message in self.get_languages():
            if group:
                u.set_field(chat_id, 'lang', self.get_languages()[message], group=group)
                u.set_field(chat_id, 'mode', 'normal', group=group)
            else:
                u.set_field(user_id, 'lang', self.get_languages()[message], group=group)
                u.set_field(user_id, 'mode', 'normal', group=group)
            self.load_language(self.get_languages()[message])
            template = self._get_template('new_language.md')
            text = template.render(is_rtl=self.get_is_rtl())
            k = ReplyKeyboardHide()
            self.telegram_api.sendMessage(
                chat_id,
                text,
                'Markdown',
                reply_markup=k)

        else:
            if group:
                u.set_field(chat_id, 'mode', 'normal', group=True)
            else:
                u.set_field(user_id, 'mode', 'normal')
            temp = self._get_template('cant_talk_message.md')
            text = temp.render()
            self.telegram_api.sendMessage(chat_id, text, 'Markdown')

    def answer_command(self, chat_id, user):
        """
        Answers the only answer command

        :param message: User message
        :param user_id: User identifier
        :param chat_id: Chat id
        :param user: User object
        :return:
        """
        keyboard = ReplyKeyboardMarkup([['Yes'], ['No']], one_time_keyboard=True)
        text = self._get_template('question_mention.md').render()
        self.telegram_api.sendMessage(chat_id, text, reply_markup=keyboard)
        user.set_field(chat_id, 'mode', 'setonlymention', group=True)

    def language_command(self, message, user_id, chat_id, user, group=False):
        """
        Handles the Language command and sends the lis of languages

        :param message: the message sent by the user
        :param user_id: User id
        :param chat_id: Chat id
        :param user: Dict with user configuration
        :param group: Indicates if the message comes from a group
        :return: None
        """
        languages = [[lang] for lang in sorted(self.get_languages().keys())]
        keyboard = ReplyKeyboardMarkup(languages, one_time_keyboard=True)
        text = self._get_template('language_answer.md').render()
        self.telegram_api.sendMessage(chat_id, text, reply_markup=keyboard)
        if group:
            user.set_field(chat_id, 'mode', 'setlanguage', group=group)
        else:
            user.set_field(user_id, 'mode', 'setlanguage', group=group)

    def settings_command(self, message, user_id, chat_id, u, group=False):
        """
        Answers the settings command

        :param message: User message
        :param user_id: User identifier
        :param chat_id: Chat id
        :param u: Uers object
        :param group: Boolen to indicate if it's on a group
        :return: None
        """

        if group:
            text = self._get_template('question_only_mention.md').render()
            k = ReplyKeyboardMarkup([['Language'], [text]], one_time_keyboard=True)
        else:
            k = ReplyKeyboardMarkup([['Language']], one_time_keyboard=True)
        text = self._get_template('configure_question.md').render()
        self.telegram_api.sendMessage(chat_id, text, reply_markup=k)
        if group:
            identifier = chat_id
        else:
            identifier = user_id
        u.set_field(identifier, 'mode', 'settings', group=group)

    def legend_command(self, message, chat_id):
        """
        Answers the legend commands

        :param message: Legend filter message
        :param chat_id: Chat identifier
        :return: None
        """
        filt = message[8:]
        selected_keys = []
        for key in typeemoji.keys():
            if filt in key:
                selected_keys.append(key)
        selected_keys = sorted(selected_keys)
        temp = self._get_template('legend_command.md')
        template_params = {
            'typeemoji': typeemoji,
            'keys': selected_keys,
            'is_rtl': self.get_is_rtl()
        }
        text = temp.render(**template_params)
        if selected_keys:
            self.telegram_api.sendMessage(chat_id, text)
        if len(selected_keys) > 50:
            text = self._get_template('easter_egg.md').render()
            self.telegram_api.sendMessage(chat_id, text)
        elif len(selected_keys) == 0:
            text = self._get_template('no_emoji.md').render()
            self.telegram_api.sendMessage(chat_id, text)

    def search_command(self, message, user_config, chat_id):
        """
        Answers the search commands

        :param message: User message
        :param user_config: User configuration as a dict
        :param chat_id: Identifier of the chat
        :return: None
        """
        search = message[8:].replace('\n', '').replace('\r', '')
        nom = pynominatim.Nominatim()
        results = nom.query(
            search,
            acceptlanguage=user_config['lang'],
            addressdetails=True)
        if not results:
            template = self._get_template('not_found_message.md')
            text = template.render(search=search)
            self.telegram_api.sendMessage(chat_id, text, parse_mode='Markdown')
            return None
        else:
            t = _('Results for') + ' "{0}":\n\n'.format(search)
            for result in results[:10]:
                if 'osm_id' in result:
                    if result['osm_type'] == 'relation':
                        element_type = 'rel'
                    elif result['osm_type'] == 'way':
                        element_type = 'way'
                    elif result['osm_type'] == 'node':
                        element_type = 'nod'
                    try:
                        if result['osm_type'] == 'relation':
                            osm_data = getData(result['osm_id'], element_type)
                        else:
                            osm_data = getData(result['osm_id'])
                    except Exception:
                        osm_data = None
                else:
                    osm_data = None
                type = result['class'] + ':' + result['type']
                if 'address' in result:
                    country = result['address'].get('country_code', '').upper()
                if type in typeemoji and country in emojiflag:
                    t += emojiflag[country][0] + typeemoji[result['class'] + ':' + result['type']] + " " + result['display_name'] + '\n'
                elif country in emojiflag:
                    t += emojiflag[country][0] + '\xE2\x96\xB6 ' + result['display_name'] + '\n'
                elif type in typeemoji:
                    t += typeemoji[result['class'] + ':' + result['type']] + " " + result['display_name'] + '\n'
                else:
                    t += '\xE2\x96\xB6 ' + result['display_name']+'\n'
                t += '\xF0\x9F\x93\x8D [' + _('Map') + '](http://www.openstreetmap.org/?minlat={0}&maxlat={1}&minlon={2}&maxlon={3}&mlat={4}&mlon={5})\n'.format(result['boundingbox'][0],result['boundingbox'][1],result['boundingbox'][2],result['boundingbox'][3],result['lat'],result['lon'])
                if osm_data is not None and ('phone' in osm_data['tag'] or 'contact:phone' in osm_data['tag']):
                    if result.get('osm_type', '') == 'node':
                        t += _('More info') + ' /detailsnod{0}\n'.format(result['osm_id'])
                    elif result.get('osm_type', '') == 'way':
                        t += _('More info')+' /detailsway{0}\n'.format(result['osm_id'])
                    elif result.get('osm_type', '') == 'relation':
                        t += _('More info') + ' /detailsrel{0}\n'.format(result['osm_id'])
                    else:
                        t += '\n' + _('More info') + ' /details{0}'.format(result['osm_id'])
                    t += _("Phone") + " /phone{0}{1}".format(element_type, result['osm_id']) + "\n\n"
                else:
                    if 'osm_id' in result:
                        if result.get('osm_type', '') == 'node':
                            t += _('More info') + ' /detailsnod{0}\n\n'.format(result['osm_id'])
                        elif result.get('osm_type', '') == 'way':
                            t += _('More info')+' /detailsway{0}\n\n'.format(result['osm_id'])
                        elif result.get('osm_type', '') == "relation":
                            t += _('More info') + ' /detailsrel{0}\n\n'.format(result['osm_id'])
                        else:
                            t += _('More info') + ' /details{0}\n\n'.format(result['osm_id'])

            t += '\xC2\xA9' + _('OpenStreetMap contributors') + '\n'
        self.telegram_api.sendMessage(
            chat_id,
            t,
            parse_mode='Markdown',
            disable_web_page_preview=True)

    def pretty_tags(self, data, identificador, element_type, user_config, chat_id, lat=None, lon=None, link=False):
        """
        Function that generates a pretty answer from a osm data

        :param data: OSM data
        :param identificador: User identifier
        :param type: Type of element
        :param user_config: Dict of the user configuration
        :param chat_id: Chat identifier
        :param lat:
        :param lon:
        :param link:
        :return: String with the answer
        """
        preview = False
        tags = {}
        if 'tag' in data:
            tags = data['tag']
        elif 'elements' in data:
            tags = data['elements']
            min_dist = None
            nearest = None
            for element in tags:
                if 'lat' in element and 'lon' in element:
                    element_lat = element['lat']
                    element_lon = element['lon']

                    dist = math.sqrt((element_lat - lat)**2 + (element_lon - lon)**2)
                elif 'center' in element:
                    element_lat = element['center']['lat']
                    element_lon = element['center']['lon']
                    dist = math.sqrt((element_lat - lat)**2 + (element_lon - lon)**2)
                if min_dist is None:
                    identificador = element['id']
                    if element['type'] == 'node':
                        element_type = 'nod'
                    elif element['type'] == 'way':
                        element_type = 'way'
                    else:
                        element_type = 'rel'
                    nearest = element
                    min_dist = dist
                elif dist < min_dist:
                    nearest = element
                    min_dist = dist
                    identificador = element['id']
                    if element['type'] == 'node':
                        element_type = 'nod'
                    elif element['type'] == 'way':
                        element_type = 'way'
                    else:
                        element_type = 'rel'
            if nearest:
                tags = nearest['tags']
            else:
                text = self._get_template('not_found_overpass_message.md')
                self.telegram_api.sendMessage(chat_id, text, 'Markdown', disable_web_page_preview=True)
        t = ''

        if 'name' in tags:
            if not user_config['lang_set']:
                t += ' ' + _('Tags for') + ' ' + str(tags['name']) + '\n\n'
            else:
                if 'name:' + self.get_language() in tags:
                    t += ' ' + _('Tags for') + ' ' + str(tags['name:'+ self.get_language()]) + '\n\n'
                else:
                    t += _('Tags for') + ' ' + str(tags['name']) + '\n\n'
        if tags.get('admin_level') == '2' and "Europe" in tags.get("is_in:continent", ''):
            t += '\xF0\x9F\x8C\x8D ' + _('European country') + "\n"
        elif tags.get('admin_level') == '2' and "Europa" in tags.get('is_in:continent', ''):
            t += "\xF0\x9F\x8C\x8D " + _("European country") + "\n"
        elif tags.get('admin_level') == '2' and "Africa" in tags.get('is_in:continent', ''):
            t += "\xF0\x9F\x8C\x8D " + _("African country") + "\n"
        elif tags.get('admin_level') == '2' and "South America" in tags.get('is_in:continent', ''):
            t += "\xF0\x9F\x8C\x8E " + _("South american country") + "\n"
        elif tags.get('admin_level') == '2' and "Latin America" in tags.get('is_in:continent', ''):
            t += "\xF0\x9F\x8C\x8E " + _("South american country") + "\n"
        elif tags.get('admin_level') == '2' and "America del Sur" in tags.get('is_in:continent', ''):
            t += "\xF0\x9F\x8C\x8E " + _("South american country") + "\n"
        elif tags.get('admin_level') == '2' and "North America" in tags.get('is_in:continent', ''):
            t += "\xF0\x9F\x8C\x8E " + _("North american country") + "\n"
        elif tags.get('admin_level') == '2' and "Amérique du Nord" in tags.get('is_in:continent', ''):
            t += "\xF0\x9F\x8C\x8E " + _("North american country") + "\n"
        elif tags.get('admin_level') == '2' and "Central America" in tags.get('is_in:continent', ''):
            t += "\xF0\x9F\x8C\x8E " + _("Central american country") + "\n"
        elif tags.get('admin_level') == '2' and "América" in tags.get("is_in:continent", ''):
            t += "\xF0\x9F\x8C\x8E " + _("American country") + "\n"
        elif tags.get('admin_level') == '2' and "America" in tags.get("is_in:continent", ''):
            t += "\xF0\x9F\x8C\x8E " + _("American country") + "\n"
        elif tags.get('admin_level') == '2' and "Asia" in tags.get("is_in:continent", ''):
            t += "\xF0\x9F\x8C\x8F " + _("Asian country") + "\n"
        elif tags.get('admin_level') == '2' and "Oceania" in tags.get("is_in:continent", ''):
            t += "\xF0\x9F\x8C\x8F " + _("Oceanian country") + "\n"
        elif tags.get('admin_level') == '2' and "Australia" in tags.get("is_in:continent", ''):
            t += "\xF0\x9F\x8C\x8F " + _("Oceanian country") + "\n"
        elif tags.get('admin_level') == '2' and "Eurasia" in tags.get("is_in:continent", ''):
            t += "\xF0\x9F\x8C\x8D \xF0\x9F\x8C\x8F " + _("Eurasian country") + "\n"
        elif tags.get('admin_level') == '2' and "Europe; Asia" in tags.get("is_in:continent", ''):
            t += "\xF0\x9F\x8C\x8D \xF0\x9F\x8C\x8F " + _("Eurasian country") + "\n"
        if 'flag' in tags:
            t += '\xF0\x9F\x9A\xA9 {}\n'.format(tags.get('flag'))
        if 'currency' in tags:
            t += "\xF0\x9F\x92\xB5 " + str(tags['currency']) + "\n"
        if 'timezone' in tags:
            t += "\xF0\x9F\x95\x92\xF0\x9F\x8C\x90 " + str(tags['timezone']) + "\n"
        if 'addr:housenumber' and 'addr:street' in tags:
            t += '\xF0\x9F\x93\xAE ' + tags['addr:street'] + ', ' + tags['addr:housenumber'] + '\n'
        else:
            if 'addr:housenumber' in tags:
                t += '\xF0\x9F\x93\xAE ' + tags['addr:housenumber'] + '\n'
            if 'addr:street' in tags:
                t += '\xF0\x9F\x93\xAE ' + tags['addr:street'] + '\n'
        if 'addr:city' in tags:
            t += tags['addr:city'] + '\n'
        if 'addr:country' in tags:
            t += tags['addr:country'] + '\n'
        if 'phone' in tags:
            t += '\xF0\x9F\x93\x9E ' + str(tags['phone']) + '\n'
        if 'contact:phone' in tags:
            t += '\xF0\x9F\x93\x9E ' + str(tags['contact:phone']) + '\n'
        if 'fax' in tags:
            t += "\xF0\x9F\x93\xA0 " + str(tags['fax']) + "\n"
        if 'email' in tags:
            t += "\xE2\x9C\x89 " + str(tags['email']) + "\n"
        if 'website' in tags:
            preview = True
            t += "\xF0\x9F\x8C\x8D " + str(tags['website']) + "\n"
        if 'opening_hours' in tags:
            t += "\xF0\x9F\x95\x9E " + str(tags['opening_hours']) + "\n"
        if 'internet_access' in tags:
            t += "\xF0\x9F\x93\xB6 " + str(tags['internet_access']) + "\n"
        if 'wheelchair' in tags:
            t += "\xE2\x99\xBF " + str(tags['wheelchair']) + "\n"
        if 'population' in tags:
            if 'population:date' in tags:
                t += "\xF0\x9F\x91\xAA " + '{:,}'.format(int(tags['population'])) + " " + _("inhabitants") + ' ' + _('at') + ' '+ tags['population:date'] + "\n"
            else:
                t += "\xF0\x9F\x91\xAA " + '{:,}'.format(int(tags['population'])) + " " + _("inhabitants") + "\n"

        if 'ele' in tags:
            t += "\xF0\x9F\x93\x8F " + str(tags['ele']) + " " + _("meters") + "\n"
        if 'wikidata' in tags:
            preview = True
            t += "\xF0\x9F\x93\x97 https://www.wikidata.org/wiki/{0}".format(urllib.quote(tags["wikidata"])) + "\n"
        if 'wikipedia' in tags:
            preview = True
            if ":" in tags["wikipedia"]:
                lang = str(tags['wikipedia'].split(":")[0])
                term = str(tags['wikipedia'].split(":")[1])
                t += "\xF0\x9F\x93\x92 http://{0}.wikipedia.org/wiki/{1}".format(lang, urllib.quote(term)) + "\n"
            else:
                t += "\xF0\x9F\x93\x92 http://wikipedia.org/wiki/{0}".format(urllib.quote(tags["wikipedia"])) + "\n"

        t += '\n' +_('Raw data:') + ' /raw' + str(element_type) + str(identificador) + '\n'
        if link:
            if element_type == 'nod':
                t += 'http://osm.org/node/{0}\n'.format(str(identificador))
            elif element_type == 'way':
                t += 'http://osm.org/way/{0}\n'.format(str(identificador))
            else:
                t += 'http://osm.org/relation/{0}\n'.format(str(identificador))
        t += '\n\xC2\xA9 ' + _('OpenStreetMap contributors') + '\n'
        self.telegram_api.sendMessage(
            chat_id,
            t,
            'Markdown',
            disable_web_page_preview=(not preview))

    def map_command(self, message, chat_id, user_id, user, zoom=None, imgformat='png', lat=None, lon=None):
        """
        Answers the map command

        :param message:  Map command with parameters
        :param chat_id: Chat identifier
        :param user_id: User identifier
        :param user: User object
        :param zoom: Zoom level for the map
        :param imgformat: Image format
        :param lat: latitude of the center of the map
        :param lon: longitude of the center of the map
        :return:
        """
        zoom_halfside = {
            1: 2000,
            2: 95,
            3: 70,
            4: 55,
            5: 50,
            6: 35,
            7: 25,
            8: 18,
            9: 14,
            10: 8,
            11: 6,
            12: 4,
            13: 2,
            14: 1,
            15: 0.5,
            16: 0.25,
            17: 0.15,
            18: 0.07,
            19: 0.04
        }
        nom = pynominatim.Nominatim()
        message = message[4:]
        signature = self._get_template('signature.md').render()
        if lat is not None and lon is not None:
            if zoom:
                halfside = zoom_halfside[zoom]
            else:
                halfside = 0.1
            bbox = genBBOX(lat, lon, halfside)
            try:
                data = download(bbox, _, imageformat=imgformat, zoom=zoom)
                f = StringIO(data)
            except ValueError as v:
                self.telegram_api.sendMessage(chat_id, v.message)
            else:

                if imgformat == 'pdf':
                    self.telegram_api.sendDocument(chat_id, f, 'map.pdf')
                elif imgformat == 'jpeg':
                    self.telegram_api.sendPhoto(chat_id, f, signature)
                elif imgformat == 'png':
                    self.telegram_api.sendPhoto(chat_id, f, signature)
            user.set_field(user_id, 'mode', 'normal')
        else:
            if re.match(" ?(png|jpg|pdf)? ?(\d?\d)?$", message):
                m = re.match(" ?(?P<imgformat>png|jpg|pdf)? ?(?P<zoom>\d{0,2})$", message)
                zoom = m.groupdict()["zoom"]
                imgformat = m.groupdict()["imgformat"]
                text = _('Please send me your location') + " \xF0\x9F\x93\x8D " +_("to receive the map") + '.\n' +_("You can do it with the Telegram paperclip button") +" \xF0\x9F\x93\x8E."
                self.telegram_api.sendMessage(chat_id, text, 'Markdown')
                if imgformat is None:
                    imgformat = 'png'
                if zoom == '':
                    zoom = 19
                user.set_field(user_id, 'format', imgformat)
                user.set_field(user_id, 'zoom', zoom)
                user.set_field(user_id, 'mode', 'map')

            elif re.match(" -?\d+(\.\d*)?,-?\d+(\.\d*)? (png|jpg|pdf)? ?(\d?\d)?", message):
                m = re.match(" (?P<lat>-?\d+(\.\d*)?),(?P<lon>-?\d+(\.\d*)?) ?(?P<imgformat>png|jpeg|pdf)? ?(?P<zoom>\d{0,2})",message)
                lat = float(m.groupdict()['lat'])
                lon = float(m.groupdict()['lon'])
                imgformat = m.groupdict()['imgformat']
                zoom = m.groupdict()['zoom']
                bbox = genBBOX(lat, lon, 0.1)
                if imgformat is None:
                    imgformat = 'png'
                if zoom == '':
                    zoom = 19
                try:
                    user_config = user.get_user(user_id, group=False)
                    lang = gettext.translation('messages', localedir='./bot/locales/', languages=[user_config['lang'], 'en'])
                    data = download(bbox, lang.gettext, imageformat=imgformat, zoom=zoom)
                    f = StringIO(data)
                except ValueError as v:
                    self.telegram_api.sendMessage(chat_id, v.message)
                else:
                    if imgformat == 'pdf':
                        self.telegram_api.sendDocument(chat_id, f, 'map.pdf')
                    elif imgformat == 'jpeg':
                        self.telegram_api.sendPhoto(chat_id, f, signature)
                    elif imgformat == 'png':
                        self.telegram_api.sendPhoto(chat_id, f, signature)
            elif re.match(self.re_map, message):
                m = re.match(" (?P<bb1>-?\d+(\.\d*)?),(?P<bb2>-?\d+(\.\d*)?),(?P<bb3>-?\d+(\.\d*)?),(?P<bb4>-?\d+(\.\d*)?) ?(?P<format>png|jpg|pdf)? ?(?P<zoom>\d{0,2})", message)
                if m is not None:
                    bbox1 = m.groupdict()['bb1']
                    bbox2 = m.groupdict()['bb2']
                    bbox3 = m.groupdict()['bb3']
                    bbox4 = m.groupdict()['bb4']
                    imgformat = m.groupdict()['format']
                    zoom = m.groupdict()['zoom']
                    if imgformat is None:
                        imgformat = 'png'
                    if zoom == '':
                        zoom = 19
                    try:
                        data = download(
                            [bbox1, bbox2, bbox3, bbox4], _,
                            imgformat, zoom=zoom)
                        f = StringIO(data)
                    except ValueError as v:
                        self.telegram_api.sendMessage(chat_id, v.message)
                    else:
                        if imgformat == 'pdf':
                            self.telegram_api.sendDocument(chat_id, f, 'map.pdf')
                        elif imgformat == 'jpeg':
                            self.telegram_api.sendPhoto(
                                chat_id, f, signature)
                        elif imgformat == 'png':
                            self.telegram_api.sendPhoto(
                                chat_id, f, signature)
                else:
                    template = self._get_template('cant_understand_message.md')
                    text = template.render()
                    self.telegram_api.sendMessage(chat_id, text, 'Markdown')
            else:
                res = nom.query(message)
                if res:
                    bbox = res[0]['boundingbox']
                    auto_scale = getScale([bbox[0], bbox[2], bbox[1], bbox[3]])
                    try:
                        data = download([bbox[2], bbox[0], bbox[3], bbox[1]], _, scale=auto_scale)
                        f = StringIO(data)
                    except ValueError as v:
                        self.telegram_api.sendMessage(chat_id, v.message)
                    else:
                        self.telegram_api.sendPhoto(chat_id, f, signature)
                else:
                    temp = self._get_template('cant_understand_message.md')
                    text = temp.render()
                    self.telegram_api.sendMessage(chat_id, text, 'Markdown')

    def phone_command(self, message, chat_id):
        id = message[9:]
        element_type = message[6: 9]
        osm_data = getData(id, element_type)
        if not id:
            template = self._get_template('not_found_id_message.md')
            text = template.render()
            self.telegram_api.sendMessage(chat_id, text, 'Markdown')
            return None
        if 'phone' in osm_data['tag']:
            template = self._get_template('phone_message.md')
            text = template.render(phone=osm_data['tag']['phone'], is_rtl=self.get_is_rtl())
            self.telegram_api.sendMessage(chat_id, text, 'Markdown')
        if 'contact:phone' in osm_data['tag'] and tags.get('phone') != tags.get('contact:phone'):
            template = self._get_template('phone_message.md')
            text = template.render(phone=osm_data['tag']['contact:phone'], is_rtl=self.get_is_rtl())
            self.telegram_api.sendMessage(chat_id, text, 'Markdown')

    @staticmethod
    def clean_message(message):
        """
        Function that cleans a message removing de @osmbot mention and \r,\n

        :param message: Message as string
        :return: Cleaned message as string
        """
        if message.startswith('@osmbot'):
            message = message[8:]
        message = message.replace('\n', '').replace('\r', '')
        return message

    def details_command(self, message, user_config, chat_id):
        """
        Answers the details command

        :param message: Message with de details command as str
        :param user_config: User config as a dict
        :param chat_id: Chat id
        :return: None
        """
        preview = False
        result = re.match('/details\s*(?P<type>nod|way|rel)\s*(?P<id>\d*)', message)
        if not result:
            text = self._get_template('not_found_id_message.md').render()
            self.telegram_api.sendMessage(
                chat_id,
                text,
                disable_web_page_preview=(not preview)
            )
            return None
        params = result.groupdict()
        element_type = params['type']
        identifier = params['id']
        if element_type in ['nod', 'way', 'rel']:
            osm_data = getData(identifier, geom_type=element_type)
        else:
            osm_data = getData(identifier)
        if osm_data is None:
            text = self._get_template('not_found_id_message.md').render()
            self.telegram_api.sendMessage(
                chat_id,
                text,
                disable_web_page_preview=(not preview)
            )
        else:
            if osm_data['tag'] == {}:
                text = self._get_template('not_recognized_message.md').render()
                self.telegram_api.sendMessage(chat_id, text, 'Markdown')
            else:
                preview = False
                if 'website' in osm_data['tag'] or 'wikidata' in osm_data['tag'] or 'wikipedia' in osm_data['tag']:
                    preview = True
                template = self._get_template('details_message.md')
                template_params = {
                    'data': osm_data,
                    'type': element_type,
                    'identifier': identifier,
                    'user_config': user_config,
                    'is_rtl': self.get_is_rtl()
                }
                text = template.render(**template_params)
                self.telegram_api.sendMessage(
                    chat_id,
                    text,
                    disable_web_page_preview=(not preview),
                    parse_mode='Markdown')

    def nearest_command(self, message, chat_id, user_id, user, config=None, lat=None, lon=None, type=None, distance=None):
        """
        Answers nearest command if lat & lon are none asks for position

        :param message: User mesage
        :param chat_id: Chat id
        :param user_id: User id
        :param user: User object
        :param config: User configuration
        :param lat: User latitude
        :param lon: User longitude
        :param type: Element type
        :param distance: Range of distance to search
        :return: None
        """
        if lat is not None and lon is not None:
            api = overpass.API()
            query = type_query[type.encode('unicode_escape')]['query']
            bbox = 'around:{0},{1},{2}'.format(distance, lat, lon)
            query = query.format(bbox)
            query = '({});out body center;'.format(query)
            data = api.Get(query.format(bbox))

            user.set_field(user_id, 'mode', 'normal')
            self.pretty_tags(data, chat_id, type, config, chat_id, lat=lat, lon=lon, link=True)
            return None
        else:
            t = message.replace('/nearest', '').strip().split(' ')[0]
            if t.encode('unicode_escape') not in type_query:
                text = self._get_template('not_implemented_message.md').render()
                self.telegram_api.sendMessage(chat_id, text, 'Markdown')
                return None

            if len(message) == 3:
                if message[2].lower()[-2:] == 'km':
                    distance = int(message[:-1]) * 1000
                elif message[2].lower()[-1:] == 'm':
                    distance = int(message[:-1])
                else:
                    distance = int(message)
            else:
                distance = type_query[t.encode('unicode_escape')]['distance']
                user.set_field(user_id, 'type', unicode(t))
                user.set_field(user_id, 'distance', str(distance))
                user.set_field(user_id, 'mode', 'nearest')
            text = self._get_template('send_location_message.md').render()
            self.telegram_api.sendMessage(chat_id, text, 'Markdown')
            return None

    def raw_command(self, message, chat_id):
        """
        Answers the raw command

        :param message: User message
        :param chat_id: Chat id
        :return: None
        """

        type = message[4:7]
        if type in ['nod', 'way', 'rel']:
            identificador = message[7:]
            osm_data = getData(identificador, geom_type=type)
        else:
            identificador = message[7:].strip()
            osm_data = getData(identificador)
        if osm_data is None:
            text = self._get_template('not_found_id_message.md').render()
            self.telegram_api.sendMessage(text, chat_id, 'Markdown', False)
        else:
            if osm_data['tag'] == {}:
                self.telegram_api.sendMessage(
                    chat_id,
                    _("Sorry, but now I can't recognize tags for this element, perhaps with my new features I will do it") +' \xF0\x9F\x98\x8B',
                    'Markdown',
                    True
                )
            else:
                parts = 1
                max_parts = 1+len(osm_data['tag'])/20
                if 'name' in osm_data['tag']:
                    t = '\xE2\x9C\x8F '+_('Raw data for')+' {0} ({1}/{2})\n\n'.format(osm_data['tag']['name'], parts, max_parts)
                else:
                    t = '\xE2\x9C\x8F '+_('Raw data') + '({0}/{1})\n\n'.format(parts, max_parts)
                i = 0
                for tag in sorted(osm_data['tag'].keys()):
                    t += "{0} = {1}\n".format(tag, osm_data['tag'][tag])
                    i += 1
                    if i >= 20:
                        t += "\n\xC2\xA9 " + _("OpenStreetMap contributors")
                        self.telegram_api.sendMessage(chat_id, t)
                        i = 0
                        parts += 1
                        if 'name' in osm_data['tag']:
                            t = '\xE2\x9C\x8F '+_('Raw data for')+' {0} ({1}/{2})\n\n'.format(osm_data['tag']['name'], parts, max_parts)
                        else:
                            t = '\xE2\x9C\x8F '+_('Raw data') + '({0}/{1})\n\n'.format(parts, max_parts)
                t += '\n\xC2\xA9 ' + _('OpenStreetMap contributors')
                self.telegram_api.sendMessage(chat_id, t)

    def answer_inline(self, message, query, user_config):
        """
        Answers the inline queryes

        :param message: User inline search
        :param query: Dict with the full query as a dict
        :param user_config: User configuration as a dict
        :return: None
        """
        if not message:
            return None
        nom = pynominatim.Nominatim()
        is_rtl = user_config['lang'] in self.get_rtl_languages()
        search_results = nom.query(message, acceptlanguage=user_config['lang'])
        temp = self._get_template('inline_article.md')
        inline_query_id = query['inline_query']['id']
        results = []
        if search_results:
            for index, r in enumerate(search_results[:7]):
                element_type = ''
                if r.get('osm_type', '') == 'node':
                    element_type = 'nod'
                elif r.get('osm_type', '') == 'way':
                    element_type = 'way'
                elif r.get('osm_type', '') == 'relation':
                    element_type = 'rel'
                osm_data = getData(r['osm_id'], geom_type=element_type)
                params = {
                    'data': osm_data, 'type': element_type,
                    'identifier': r['osm_id'], 'user_config': user_config,
                    'is_rtl': is_rtl, 'nominatim_data': r
                }
                if osm_data:
                    text = temp.render(**params)
                name_lang = 'name:{}'.format(user_config['lang'])
                if name_lang in osm_data['tag']:
                    results.append(InlineQueryResultArticle(
                        id=uuid4(),
                        title=osm_data['tag'][name_lang],
                        description=r['display_name'],
                        input_message_content=InputTextMessageContent(
                            text,
                            parse_mode=ParseMode.MARKDOWN)))
                else:
                    results.append(InlineQueryResultArticle(
                        id=uuid4(),
                        title=osm_data['tag']['name'],
                        description=r['display_name'],
                        input_message_content=InputTextMessageContent(
                            text,
                            parse_mode=ParseMode.MARKDOWN)))

        self.telegram_api.answerInlineQuery(
            inline_query_id,
            results,
            is_personal=True,
            cache_time=86400)

    def answer_message(self, message, query, chat_id, user_id, user_config, is_group, user, message_type):
        """
        Function that handles messages and sends to the concrete functions

        :param message: User message
        :param query: Dict with the full query
        :param chat_id: Chat id
        :param user_id: User id
        :param user_config: Dict with the user config
        :param is_group: Boolean that indicates if the message comes from
        a group
        :param user: User object
        :param message_type: Type of message
        :return: None
        """
        if message_type == 'inline':
            self.answer_inline(message, query, user_config)
        else:
            preview = False
            if message.lower() == '/start':
                user.set_field(chat_id, 'mode', 'normal')
                text = self._get_template('start_answer.md').render()
                self.telegram_api.sendMessage(
                    chat_id,
                    text,
                    'Markdown',
                    (not preview))
            elif 'location' in query['message']:
                if user_config is not None and user_config.get('mode', '') == 'map':
                    self.map_command(
                        message, chat_id, user_id, user, zoom=user_config["zoom"],
                        imgformat=user_config['format'],
                        lat=float(query['message']['location']['latitude']),
                        lon=float(query['message']['location']['longitude']))
                elif user_config.get('mode', '') == 'nearest':
                    self.nearest_command(
                        message, chat_id, user_id, user,
                        lat=float(query['message']['location']['latitude']),
                        lon=float(query['message']['location']['longitude']),
                        distance=user_config['distance'],
                        type=user_config['type'],
                        config=user_config
                    )
            elif user_config['mode'] == 'settings':
                if message == 'Language':
                    self.language_command(
                        message, user_id, chat_id, user, is_group)
                elif message == 'Answer only when mention?':
                    self.answer_command(chat_id, user)
                else:
                    template_name = 'seting_not_recognized_message.md'
                    temp = self._get_template(template_name)
                    text = temp.render()
                    self.telegram_api.sendMessage(chat_id, text, 'Markdown', not preview)
                    user.set_field(chat_id, 'mode', 'normal', group=is_group)
            elif user_config['mode'] == 'setlanguage':
                self.set_language_command(
                    message, user_id, chat_id, user, is_group)
            elif user_config['mode'] == 'setonlymention':
                self.set_only_mention(message, user_id, chat_id, user, is_group)
            elif 'text' in query['message']:
                if re.match(".*geo:-?\d+(\.\d*)?,-?\d+(\.\d*)?", message) is not None and user_config.get('mode', '') == 'map':
                    m = re.match(
                        ".*geo:(?P<lat>-?\d+(\.\d*)?),(?P<lon>-?\d+(\.\d*)?).*",
                        message)
                    lat = m.groupdict()['lat']
                    lon = m.groupdict()['lon']
                    self.map_command(
                        message, chat_id, user_id, user,
                        zoom=user_config['zoom'],
                        imgformat=user_config['format'],
                        lat=float(lat), lon=float(lon))
                elif message == 'Language':
                    self.language_command(message, user_id, chat_id, user, is_group)
                elif message == 'Answer only when mention?':
                    self.answer_command(chat_id, user)
                elif message.lower().startswith('/settings'):
                    self.settings_command(message, user_id, chat_id, user, is_group)
                elif message.lower().startswith('/nearest'):
                    self.nearest_command(message, chat_id, user_id, user)
                elif message.lower().startswith('/map'):
                    self.map_command(message, chat_id, user_id, user)
                elif re.match('/phone.*', message.lower()):
                    self.phone_command(message, chat_id)
                elif re.match('/details.*', message.lower()):
                    try:
                        self.details_command(message, user_config, chat_id)
                    except Exception as e:
                        print(e.message)
                elif re.match("/raw.*", message.lower()):
                    try:
                        self.raw_command(message, chat_id)
                    except Exception as e:
                        print(e.message)
                        import traceback
                        print(traceback.format_exc())
                        pass
                elif message.lower().startswith('/legend'):
                    self.legend_command(message, chat_id)
                elif message.lower().startswith('/about'):
                    is_rtl = self.get_is_rtl()
                    template = self._get_template('about_answer.md')
                    text = template.render(is_rtl=is_rtl)
                    self.telegram_api.sendMessage(chat_id, text, 'Markdown', not preview)
                elif message.lower().startswith('/help'):
                    template = self._get_template('help_message.md')
                    text = template.render(is_rtl=self.get_is_rtl()).replace('_', '\_')
                    self.telegram_api.sendMessage(chat_id, text, 'Markdown')
                elif re.match('/search.*', message.lower()) is not None and message[8:] != '':
                    self.search_command(message, user_config, chat_id)
                elif re.match('/search', message.lower()) is not None:
                    text = _('Please indicate what are you searching with command /search <search_term>')
                    self.telegram_api.sendMessage(chat_id, text, 'Markdown')
                else:
                    text = _('Use /search <search\_term> command to indicate what you are searching')
                    self.telegram_api.sendMessage(chat_id, text, 'Markdown')
