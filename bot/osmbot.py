# -*- coding: UTF-8 -*-
from __future__ import absolute_import

from bot.bot import Bot, Message, ReplyKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
import os
from jinja2 import Environment
import urllib
import math
import re
from bot.typeemoji import typeemoji
import bot.user as u
import gettext
import pynominatim
from bot.maptools import download, genBBOX, getScale
from bot.utils import getData
from bot.overpass_query import type_query
import overpass


def url_escape(s):
    """
    Used to escape URL in template

    :param s: original URL in data
    :return: Well fomrated URL
    """
    return s.replace(' ', '%20').replace(')', '\\)')


class OsmBot(object):
    """
        Class that represents the OsmBot
    """
    def __init__(self, config):
        """
        Class constructor

        :param config: Dictionary with the configuration variables (token,host,database,user,password)
        """
        self.avaible_languages = {
            'Catalan': 'ca', 'English': 'en', 'Spanish': 'es', 'Swedish': 'sv',
            'Asturian': 'ast', 'Galician': 'gl', 'French': 'fr',
            'Italian': 'it',
            'Basque': 'eu', 'Polish': 'pl', 'German': 'de', 'Dutch': 'nl',
            'Czech': 'cs', 'Persian': 'fa', 'Japanese': 'ja', 'Ukrainian': 'uk',
            'Chinese (Taiwan)': 'zh_TW', 'Vietnamese': 'vi', 'Russian': 'ru',
            'Slovak': 'sk', 'Chinese (Hong Kong)': 'zh_HK', 'Hungarian': 'hu'
        }
        self.rtl_languages = ['fa']
        token = config.get('token', '')
        if config:
            self.user = u.User(config.get('host', ''), config.get('database', ''),
                          config.get('user', ''), config.get('password', ''))
        self.bot = Bot(token)
        self.jinja_env = Environment(extensions=['jinja2.ext.i18n'])
        self.jinja_env.filters['url_escape'] = url_escape
        self.language = None

    def load_language(self, language):
        """
        Function to load the language of the answer

        :param language: code of the language
        :return: None
        """
        self.language = language
        lang = gettext.translation('messages', localedir='./bot/locales/', languages=[language, 'en'])
        lang.install()
        self.jinja_env.install_gettext_translations(gettext.translation('messages', localedir='./bot/locales/',languages=[language, 'en']))

    def get_is_rtl(self):
        """
        Returns if the actual language is RTL

        :return: Boolean to indicate if the language is RTL
        """
        return  self.language in self.rtl_languages

    def get_language(self):
        """
        Retunrs the actual language code

        :return: str Language code
        """
        return self.language

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

    def SetOnlyMention(self, message, user_id, chat_id, user, group):
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
            m = Message(chat_id, text)
            self.bot.sendMessage(m)
        else:
            text = self._get_template('answer_always.md').render()
            m = Message(chat_id, text)
            self.bot.sendMessage(m)
        return []

    def SetLanguageCommand(self, message, user_id, chat_id, u, group=False):
        if message in self.get_languages():
            if group:
                u.set_field(chat_id, 'lang', self.get_languages()[message], group=group)
                u.set_field(chat_id, 'mode', 'normal', group=group)
            else:
                u.set_field(user_id, 'lang', self.get_languages()[message], group=group)
                u.set_field(user_id, 'mode', 'normal', group=group)
            self.load_language(self.get_languages()[message])
            text = self._get_template('new_language.md').render()
            m = Message(chat_id, text)
            self.bot.sendMessage(m)
            return []
        else:
            if group:
                u.set_field(chat_id, 'mode', 'normal', group=True)
            else:
                u.set_field(user_id, 'mode', 'normal')
            temp = self._get_template('cant_talk_message.md')
            text = temp.render()
            message = Message(chat_id, text)
            self.bot.sendMessage(message)
            return []

    def AnswerCommand(self, message, user_id, chat_id, user):
        k = ReplyKeyboardMarkup(['Yes','No'], one_time_keyboard=True)
        text = self._get_template('question_mention.md').render()
        m = Message(chat_id, text, reply_markup=k)
        self.bot.sendMessage(m)
        user.set_field(chat_id, 'mode', 'setonlymention', group=True)

    def LanguageCommand(self, message, user_id, chat_id, user, group=False):
        k = ReplyKeyboardMarkup(
            sorted(self.get_languages().keys()),
            one_time_keyboard=True)
        text = self._get_template('language_answer.md').render()
        m = Message(chat_id, text, reply_markup=k)
        self.bot.sendMessage(m)
        if group:
            user.set_field(chat_id, 'mode', 'setlanguage', group=group)
        else:
            user.set_field(user_id, 'mode', 'setlanguage', group=group)
        return []

    def SettingsCommand(self, message, user_id, chat_id, u, group=False):
        k = ReplyKeyboardMarkup(['Language'], one_time_keyboard=True)
        if group:
            text = self._get_template('question_only_mention.md').render()
            k.addButton(text)
        text = self._get_template('configure_question.md').render()
        m = Message(chat_id, text, reply_markup=k)
        self.bot.sendMessage(m)
        if group:
            identifier = chat_id
        else:
            identifier = user_id
        u.set_field(identifier, 'mode', 'settings', group=group)

    def LegendCommand(self, message, chat_id):
        filt = message[8:]
        selected_keys = []
        for key in typeemoji.keys():
            if filt in key:
                selected_keys.append(key)
        selected_keys = sorted(selected_keys)
        temp = self._get_template('legend_command.md')
        text = temp.render(typeemoji=typeemoji, keys=selected_keys)
        m = Message(chat_id, text)
        self.bot.sendMessage(m)
        if len(selected_keys) > 50:
            text = self._get_template('easter_egg.md').render()
            m = Message(chat_id, text)
            self.bot.sendMessage(m)
        elif len(selected_keys) == 0:
            text = self._get_template('no_emoji.md').render()
            m = Message(chat_id, text)
            self.bot.sendMessage(m)

    def SearchCommand(self, message, user_config, chat_id):
        import pynominatim
        t = ''
        search = message[8:].replace('\n', '').replace('\r', '')
        nom = pynominatim.Nominatim()
        results = nom.query(search,acceptlanguage=user_config['lang'])
        if not results:
            text = self._get_template('not_found_message.md').render(search=search)
            m = Message(chat_id, text)
            self.bot.sendMessage(m)
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
                if type in typeemoji:
                    t += typeemoji[result['class'] + ':' + result['type']] + " " + result['display_name'] + '\n'
                else:
                    t += '\xE2\x96\xB6 ' + result['display_name']+'\n'
                t += '\xF0\x9F\x93\x8D [' + _('Map') + '](http://www.openstreetmap.org/?minlat={0}&maxlat={1}&minlon={2}&maxlon={3}&mlat={4}&mlon={5})\n'.format(result['boundingbox'][0],result['boundingbox'][1],result['boundingbox'][2],result['boundingbox'][3],result['lat'],result['lon'])
                if osm_data is not None and ('phone' in osm_data['tag'] or 'contact:phone' in osm_data['tag']):
                    if 'osm_type' in result and result['osm_type'] == 'node':
                        t += _('More info') + ' /detailsnod{0}\n'.format(result['osm_id'])
                    elif 'osm_type' in result and result['osm_type'] == 'way':
                        t += _('More info')+' /detailsway{0}\n'.format(result['osm_id'])
                    elif 'osm_type' in result and result['osm_type'] == 'relation':
                        t += _('More info') + ' /detailsrel{0}\n'.format(result['osm_id'])
                    else:
                        t += '\n' + _('More info') + ' /details{0}'.format(result['osm_id'])
                    t += _("Phone") + " /phone{0}{1}".format(element_type, result['osm_id']) + "\n\n"
                else:
                    if 'osm_id' in result:
                        if 'osm_type' in result and result['osm_type'] == 'node':
                            t += _('More info') + ' /detailsnod{0}\n\n'.format(result['osm_id'])
                        elif 'osm_type' in result and result['osm_type'] == 'way':
                            t += _('More info')+' /detailsway{0}\n\n'.format(result['osm_id'])
                        elif 'osm_type' in result and result['osm_type'] =="relation":
                            t += _('More info') + ' /detailsrel{0}\n\n'.format(result['osm_id'])
                        else:
                            t += _('More info') + ' /details{0}\n\n'.format(result['osm_id'])

            t += '\xC2\xA9' + _('OpenStreetMap contributors') + '\n'
        m = Message(chat_id, t, parse_mode='Markdown')
        self.bot.sendMessage(m)

    def pretty_tags(self, data, identificador, type, user_config, chat_id, lat=None, lon=None, link=False):
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
                        type = 'nod'
                    elif element['type'] == 'way':
                        type = 'way'
                    else:
                        type = 'rel'
                    nearest = element
                    min_dist = dist
                elif dist < min_dist:
                    nearest = element
                    min_dist = dist
                    identificador = element['id']
                    if element['type'] == 'node':
                        type = 'nod'
                    elif element['type'] == 'way':
                        type = 'way'
                    else:
                        type = 'rel'
            if nearest:
                tags = nearest['tags']
            else:
                text = self._get_template('not_found_overpass_message.md')
                m = Message(
                    chat_id,
                    text,
                    disable_web_page_preview=True
                )
                self.bot.sendMessage(m)
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

        t += '\n' +_('Raw data:') + ' /raw' + str(type) + str(identificador) + '\n'
        if link:
            if type == 'nod':
                t += 'http://osm.org/node/{0}\n'.format(str(identificador))
            elif type == 'way':
                t += 'http://osm.org/way/{0}\n'.format(str(identificador))
            else:
                t += 'http://osm.org/relation/{0}\n'.format(str(identificador))
        t += '\n\xC2\xA9 ' + _('OpenStreetMap contributors') + '\n'

        m = Message(chat_id, t, disable_web_page_preview=(not preview))
        self.bot.sendMessage(m)

    def MapCommand(self, message, chat_id, user_id, user, zoom=None, imgformat='png', lat=None, lon=None):
        nom = pynominatim.Nominatim()
        response = []
        message = message[4:]
        if lat is not None and lon is not None:
            bbox = genBBOX(lat, lon, 0.1)
            try:
                data = download(bbox, _, imageformat=imgformat, zoom=zoom)
            except ValueError as v:
                response.append(Message(chat_id, v.message))
            else:
                if imgformat == 'pdf':
                    self.bot.sendDocument(chat_id, data, 'map.pdf')
                elif imgformat == 'jpeg':
                    self.bot.sendPhoto(chat_id, data, 'map.jpg', '©' + _('OSM contributors'))
                elif imgformat == 'png':
                    self.bot.sendPhoto(chat_id, data, 'map.png', '©' + _('OSM contributors'))
            user.set_field(user_id, 'mode', 'normal')
        else:
            if re.match(" ?(png|jpg|pdf)? ?(\d?\d)?$", message):
                m = re.match(" ?(?P<imgformat>png|jpg|pdf)? ?(?P<zoom>\d{0,2})$", message)
                zoom = m.groupdict()["zoom"]
                imgformat = m.groupdict()["imgformat"]
                m = Message(
                    chat_id,
                    _('Please send me your location') + " \xF0\x9F\x93\x8D " +
                    _("to receive the map.") + '.\n' +
                    _("You can do it with the Telegram paperclip button") +
                    " \xF0\x9F\x93\x8E."
                            )
                response.append(m)
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
                except ValueError as v:
                    response.append(v.message)
                else:
                    if imgformat == 'pdf':
                        self.bot.sendDocument(chat_id, data, 'map.pdf')
                    elif imgformat == 'jpeg':
                        self.bot.sendPhoto(
                            chat_id, data, 'map.jpg', '©' + _('OSM contributors'))
                    elif imgformat == 'png':
                        self.bot.sendPhoto(
                            chat_id, data, 'map.png', '©' + _('OSM contributors'))
            elif re.match(" -?\d+(\.\d*)?,-?\d+(\.\d*)?,-?\d+(\.\d*)?,-?\d+(\.\d*)? ?(png|jpeg|pdf)? ?\d{0,2}",message):
                m = re.match(" (?P<bb1>-?\d+(\.\d*)?),(?P<bb2>-?\d+(\.\d*)?),(?P<bb3>-?\d+(\.\d*)?),(?P<bb4>-?\d+(\.\d*)?) ?(?P<format>png|jpg|pdf)? ?(?P<zoom>\d{0,2})",message)
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
                    except ValueError as v:
                        response.append(v.message)
                    else:
                        if imgformat == 'pdf':
                            self.bot.sendDocument(chat_id, data, 'map.pdf')
                        elif imgformat == 'jpeg':
                            self.bot.sendPhoto(
                                chat_id, data, 'map.jpg', '©' + _('OSM contributors'))
                        elif imgformat == 'png':
                            self.bot.sendPhoto(
                                chat_id, data, 'map.png', '©' + _('OSM contributors'))
                else:
                    text = self._get_template('cant_understand_message.md').render()
                    response.append(text)
            else:
                res = nom.query(message)
                if res:
                    bbox = res[0]['boundingbox']
                    auto_scale = getScale([bbox[0], bbox[2], bbox[1], bbox[3]])
                    try:
                        data = download([bbox[2], bbox[0], bbox[3], bbox[1]], _, scale=auto_scale )
                    except ValueError as v:
                        m = Message(chat_id, v.message)
                        response.append(m)
                    else:
                        self.bot.sendPhoto(chat_id, data, 'map.png', '©' + _('OSM contributors'))
                else:
                    temp = self._get_template('cant_understand_message.md')
                    text = temp.render()
                    m = Message(chat_id, text)
                    response.append(m)
        self.bot.sendMessage(response)

    def PhoneCommand(self, message, chat_id):
        id = message[9:]
        element_type = message[6: 9]
        osm_data = getData(id, element_type)
        if 'phone' in osm_data['tag']:
            template = self._get_template('phone_message.md')
            text = template.render(phone=osm_data['tag']['phone'])
            m = Message(chat_id, text)
            self.bot.sendMessage(m)
        if 'contact:phone' in osm_data['tag']:
            template = self._get_template('phone_message.md')
            text = template.render(phone=osm_data['tag']['contact:phone'])
            m = Message(chat_id, text)
            self.bot.sendMessage(m)

    def CleanMessage(self, message):
        if message.startswith('@osmbot'):
            message = message[8:]
        message = message.replace('\n', '').replace('\r', '')
        return message

    def DetailsCommand(self, message, user_config, chat_id):
        preview = False
        result = re.match('/details\s*(?P<type>nod|way|rel)\s*(?P<id>\d*)', message)
        if not result:
            text = self._get_template('not_found_id_message.md').render()
            m = Message(
                chat_id,
                text,
                disable_web_page_preview=(not preview)
            )
            self.bot.sendMessage(m)
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
            m = Message(
                chat_id,
                text,
                disable_web_page_preview=(not preview)
            )
            self.bot.sendMessage(m)
        else:
            if osm_data['tag'] == {}:
                text = self._get_template('not_recognized_message.md').render()
                m = Message(chat_id, text)
                self.bot.sendMessage(m)
            else:
                preview = False
                if 'website' in osm_data['tag'] or 'wikidata' in osm_data['tag'] or 'wikipedia' in osm_data['tag']:
                    preview = True
                text = self._get_template('details_message.md').render(data=osm_data, type=element_type, identifier=identifier, user_config=user_config)
                m = Message(chat_id, text, disable_web_page_preview=(not preview), parse_mode='Markdown')
                self.bot.sendMessage(m)

    def NearestCommand(self, message, chat_id, user_id, user, config=None, lat=None, lon=None, type=None, distance=None):
        if lat is not None and lon is not None:
            api = overpass.API()
            query = type_query[type.encode('unicode_escape')]['query']
            bbox = 'around:{0},{1},{2}'.format(distance, lat, lon)
            query = query.format(bbox)
            query = '({});out body center;'.format(query)
            data = api.Get(query.format(bbox))

            user.set_field(user_id, 'mode', 'normal')
            self.pretty_tags(data, chat_id, type, config, chat_id, lat=lat, lon=lon, link=True)

        else:
            t = message.replace('/nearest', '').strip().split(' ')[0]
            if t.encode('unicode_escape') not in type_query:
                text = self._get_template('not_implemented_message.md').render()
                m = Message(chat_id, text)
                self.bot.sendMessage(m)

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
            m = Message(chat_id, text)
            self.bot.sendMessage(m)

    def RawCommand(self, message, chat_id):
        type = message[4:7]
        if type == 'nod' or type == 'way' or type == 'rel':
            identificador = message[7:]
            osm_data = getData(identificador, geom_type=type)
        else:
            identificador = message[7:].strip()
            osm_data = getData(identificador)
        if osm_data is None:
            text = self._get_template('not_found_id_message.md').render()
            m = Message(chat_id, text)
            self.bot.sendMessage(m)
        else:
            if osm_data['tag'] == {}:
                m = Message(
                    chat_id,
                    _("Sorry, but now I can't recognize tags for this element, perhaps with my new features I will do it") +
                    ' \xF0\x9F\x98\x8B'
                )
                self.bot.sendMessage(m)
            else:
                parts = 1
                max_parts = 1+len(osm_data['tag'])/20
                if 'name' in osm_data['tag']:
                    t = '\xE2\x9C\x8F '+_('Raw data for')+' {0} ({1}/{2})\n\n'.format(osm_data['tag']['name'], parts, max_parts)
                else:
                    t = '\xE2\x9C\x8F '+_('Raw data') + '({0}/{1})\n\n'.format(parts, max_parts)
                i = 0
                response = []
                for tag in sorted(osm_data['tag'].keys()):
                    t += "{0} = {1}\n".format(tag, osm_data['tag'][tag])
                    i += 1
                    if i >= 20:
                        t += "\n\xC2\xA9 " + _("OpenStreetMap contributors")
                        m = Message(chat_id, t)
                        response.append(m)
                        i = 0
                        parts += 1
                        if 'name' in osm_data['tag']:
                            t = '\xE2\x9C\x8F '+_('Raw data for')+' {0} ({1}/{2})\n\n'.format(osm_data['tag']['name'], parts, max_parts)
                        else:
                            t = '\xE2\x9C\x8F '+_('Raw data') + '({0}/{1})\n\n'.format(parts, max_parts)
                t += '\n\xC2\xA9 ' + _('OpenStreetMap contributors')
                m = Message(chat_id, t)
                response.append(m)
                self.bot.sendMessage(response)

    def answer_inline(self, message, query, chat_id, user_id, user_config, is_group, user):
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
                    'is_rtl': is_rtl
                }
                if osm_data:
                    text = temp.render(**params)
                answer = InputTextMessageContent(text, 'Markdown')
                result = InlineQueryResultArticle('article', '{}/{}'.format(inline_query_id, index), title=r['display_name'], input_message_content=answer)
                results.append(result)
        self.bot.answerInlineQuery(inline_query_id, results, is_personal=True, cache_time=86400)

    def answer_message(self, message, query, chat_id, user_id, user_config, is_group, user, message_type):
        if message_type == 'inline':
            self.answer_inline(message, query, chat_id, user_id, user_config, is_group, user)
        else:
            preview = False
            response = []
            if message.lower() == '/start':
                user.set_field(chat_id, 'mode', 'normal')
                text = self._get_template('start_answer.md').render()
                m = Message(
                    chat_id, text,
                    disable_web_page_preview=(not preview),
                    parse_mode='Markdown')
                self.bot.sendMessage(m)
            elif 'location' in query['message']:
                if user_config is not None and 'mode' in user_config and user_config['mode'] == 'map':
                    self.MapCommand(
                        message, chat_id, user_id, user, zoom=user_config["zoom"],
                        imgformat=user_config['format'],
                        lat=float(query['message']['location']['latitude']),
                        lon=float(query['message']['location']['longitude']))
                elif user_config.get('mode', None) == 'nearest':
                    self.NearestCommand(
                        message, chat_id, user_id, user,
                        lat=float(query['message']['location']['latitude']),
                        lon=float(query['message']['location']['longitude']),
                        distance=user_config['distance'],
                        type=user_config['type'],
                        config=user_config
                    )
            elif user_config['mode'] == 'settings':
                if message == 'Language':
                    self.LanguageCommand(
                        message, user_id, chat_id, user, is_group)
                elif message == 'Answer only when mention?':
                    self.AnswerCommand(message, user_id, chat_id, user)
                else:
                    template_name = 'seting_not_recognized_message.md'
                    temp = self._get_template(template_name)
                    text = temp.render()
                    m = Message(
                        chat_id, text, disable_web_page_preview=(not preview),
                        parse_mode='Markdown'
                    )
                    self.bot.sendMessage(m)
                    user.set_field(chat_id, 'mode', 'normal', group=is_group)
            elif user_config['mode'] == 'setlanguage':
                self.SetLanguageCommand(
                    message, user_id, chat_id, user, is_group)
            elif user_config['mode'] == 'setonlymention':
                response += self.SetOnlyMention(message, user_id, chat_id, user, is_group)
            elif 'text' in query['message']:
                if re.match(".*geo:-?\d+(\.\d*)?,-?\d+(\.\d*)?", message) is not None and "mode" in user_config and user_config['mode'] == 'map':
                    m = re.match(
                        ".*geo:(?P<lat>-?\d+(\.\d*)?),(?P<lon>-?\d+(\.\d*)?).*",
                        message)
                    lat = m.groupdict()['lat']
                    lon = m.groupdict()['lon']
                    response += self.MapCommand(
                        message, chat_id, user_id, user,
                        zoom=user_config['zoom'],
                        imgformat=user_config['format'],
                        lat=float(lat), lon=float(lon))
                elif message == 'Language':
                    response += self.LanguageCommand(message, user_id, chat_id, user,
                                                is_group)
                elif message == 'Answer only when mention?':
                    response += self.AnswerCommand(message, user_id, chat_id, user)
                elif message.lower().startswith('/settings'):
                    self.SettingsCommand(message, user_id, chat_id, user, is_group)
                elif message.lower().startswith('/nearest'):
                    self.NearestCommand(message, chat_id, user_id, user)
                elif message.lower().startswith('/map'):
                    self.MapCommand(message, chat_id, user_id, user)
                elif re.match('/phone.*', message.lower()):
                    self.PhoneCommand(message, chat_id)
                elif re.match('/details.*', message.lower()):
                    try:
                        self.DetailsCommand(message, user_config, chat_id)
                    except Exception as e:
                        print e.message
                elif re.match("/raw.*", message.lower()):
                    try:
                        self.RawCommand(message, chat_id)
                    except Exception as e:
                        print(e.message)
                        import traceback
                        print(traceback.format_exc())
                        pass
                elif message.lower().startswith('/legend'):
                    self.LegendCommand(message, chat_id)
                elif message.lower().startswith('/about'):
                    is_rtl = self.get_is_rtl()
                    template = self._get_template('about_answer.md')
                    text = template.render(is_rtl=is_rtl)
                    m = Message(
                        chat_id, text,
                        disable_web_page_preview=(not preview),
                        parse_mode='Markdown')
                    self.bot.sendMessage(m)
                elif message.lower().startswith('/help'):
                    text = self._get_template('help_message.md').render()
                    response = [text]
                    response[-1] = response[-1].replace('_', '\_')
                elif re.match('/search.*', message.lower()) is not None and message[8:] != '':
                    self.SearchCommand(message, user_config, chat_id)
                elif re.match('/search', message.lower()) is not None:
                    m = Message(
                        chat_id,
                        _('Please indicate what are you searching with command /search <search_term>')
                    )
                    self.bot.sendMessage(m)
                else:
                    m = Message(
                        chat_id,
                        _('Use /search <search_term> command to indicate what you are searching')
                    )
                    self.bot.sendMessage(m)
            if response:
                m = Message(
                    chat_id, response, disable_web_page_preview=(not preview),
                    parse_mode='Markdown'
                )
                self.bot.sendMessage(m)
