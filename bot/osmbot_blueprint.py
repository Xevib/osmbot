# -*- coding: utf-8 -*-
import re
import math
from flask import Flask
from flask import request, current_app, Blueprint
import pynominatim
from osmapi import OsmApi
from bot import OSMbot, Message, ReplyKeyboardHide, ReplyKeyboardMarkup, KeyboardButton, InlineQueryResultArticle, InputTextMessageContent
import urllib
from configobj import ConfigObj
from typeemoji import typeemoji
from maptools import download, genBBOX, getScale
import gettext
import overpass
from overpass_query import type_query
import user as u
from jinja2 import Environment
import os
from lxml import etree
from StringIO import StringIO

avaible_languages = {
    'Catalan': 'ca', 'English': 'en', 'Spanish': 'es', 'Swedish': 'sv',
    'Asturian': 'ast', 'Galician': 'gl', 'French': 'fr', 'Italian': 'it',
    'Basque': 'eu', 'Polish': 'pl', 'German': 'de', 'Dutch': 'nl',
    'Czech': 'cz', 'Persian': 'fa', 'Japanese': 'ja', 'Ukrainian': 'uk',
    'Chinese(Taiwan)': 'zh_TW', 'Vietnamese': 'vi'
}

application = Flask(__name__)
application.debug = True
config = ConfigObj('bot.conf')


token = config.get('token', '')
user = u.User(config.get('host',''), config.get('database', ''), config.get('user',''), config.get('password',''))
bot = OSMbot(token)
api = OsmApi()
nom = pynominatim.Nominatim()

osmbot = Blueprint(
    'osmbot', __name__,
    template_folder='templates',
    static_folder='static'
)
jinja_env = Environment(extensions=['jinja2.ext.i18n'])


def getData(id, geom_type=None):
    osm_data = None
    if geom_type is None:
        try:
            osm_data = api.NodeGet(int(id))
            if osm_data is None:
                try:
                    osm_data = api.WayGet(int(id))
                except:
                    osm_data = api.RelationGet(int(id))
        except:
            osm_data = None
    elif geom_type == 'nod':
        osm_data = api.NodeGet(int(id))
    elif geom_type == 'way':
            osm_data = api.WayGet(int(id))
    elif geom_type == 'rel':
        osm_data = api.RelationGet(int(id))
    return osm_data


def SetOnlyMention(message, user_id, chat_id, user, group):
    onlymentions = message == 'Yes'
    if group:
        user.set_field(chat_id, 'onlymentions', onlymentions, group=group)
        user.set_field(chat_id, 'mode', 'normal', group=group)
    else:
        user.set_field(user_id, 'onlymentions', onlymentions, group=group)
        user.set_field(user_id, 'mode', 'normal', group=group)
    if not onlymentions:
        text = get_template('only_mention.md').render()
        m = Message(chat_id, text)
        bot.sendMessage(m)
    else:
        text = get_template('answer_always.md').render()
        m = Message(chat_id, text)
        bot.sendMessage(m)
    return []


def SetLanguageCommand(message, user_id, chat_id, u, group=False):
    if message in avaible_languages:
        if group:
            u.set_field(chat_id, 'lang', avaible_languages[message],group=group)
            u.set_field(chat_id, 'mode', 'normal', group=group)
        else:
            u.set_field(user_id, 'lang', avaible_languages[message],group=group)
            u.set_field(user_id, 'mode', 'normal', group=group)
        text = get_template('new_language.md').render()
        m = Message(chat_id, text)
        bot.sendMessage(m)
        return []
    else:
        if group:
            u.set_field(chat_id, 'mode', 'normal', group=True)
        else:
            u.set_field(user_id, 'mode', 'normal')
        temp = get_template('cant_talk_message.md')
        text = temp.render()
        message = Message(chat_id, text)
        bot.sendMessage(message)
        return []


def AnswerCommand(message, user_id, chat_id, user):
    k = ReplyKeyboardMarkup(['Yes','No'], one_time_keyboard=True)
    text = get_template('question_mention.md').render()
    m = Message(chat_id, text, reply_markup=k)
    bot.sendMessage(m)
    user.set_field(chat_id, 'mode', 'setonlymention', group=True)


def LanguageCommand(message, user_id, chat_id, user, group=False):
    k = ReplyKeyboardMarkup(
        sorted(avaible_languages.keys()),
        one_time_keyboard=True)
    text = get_template('language_answer.md').render()
    m = Message(chat_id, text, reply_markup=k)
    bot.sendMessage(m)
    if group:
        user.set_field(chat_id, 'mode', 'setlanguage', group=group)
    else:
        user.set_field(user_id, 'mode', 'setlanguage', group=group)
    return []


def SettingsCommand(message, user_id, chat_id, u, group=False):
    k = ReplyKeyboardMarkup(['Language'], one_time_keyboard=True)
    if group:
        text = get_template('question_only_mention.md').render()
        k.addButton(text)
    text = get_template('configure_question.md').render()
    m = Message(chat_id, text, reply_markup=k)
    bot.sendMessage(m)
    if group:
        identifier = chat_id
    else:
        identifier = user_id
    u.set_field(identifier, 'mode', 'settings', group=group)


def LegendCommand(message, chat_id):
    filt = message[8:]
    selected_keys = []
    for key in typeemoji.keys():
        if filt in key:
            selected_keys.append(key)
    selected_keys = sorted(selected_keys)
    temp = get_template('legend_command.md')
    text = temp.render(typeemoji=typeemoji, keys=selected_keys)
    m = Message(chat_id, text)
    bot.sendMessage(m)
    if len(selected_keys) > 50:
        text = get_template('easter_egg.md').render()
        m = Message(chat_id, text)
        bot.sendMessage(m)
    elif len(selected_keys) == 0:
        text = get_template('no_emoji.md').render()
        m = Message(chat_id, text)
        bot.sendMessage(m)


def SearchCommand(message, user_config, chat_id):
    import pynominatim
    t = ''
    search = message[8:].replace('\n', '').replace('\r', '')
    nom = pynominatim.Nominatim()
    results = nom.query(search)
    if not results:
        text = get_template('not_found_message.md').render(search=search)
        m = Message(chat_id, text)
        bot.sendMessage(m)
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
    bot.sendMessage(m)


def pretty_tags(data, identificador, type, user_config, chat_id, lat=None, lon=None, link=False):
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
            text = get_template('not_found_overpass_message.md')
            m = Message(
                chat_id,
                text,
                disable_web_page_preview=True
            )
            bot.sendMessage(m)
    t = ''

    if 'name' in tags:
        if not user_config['lang_set']:
            t += ' ' + _('Tags for') + ' ' + str(tags['name']) + '\n\n'
        else:
            if 'name:' + str(user_config['lang']) in tags:
                t += ' ' + _('Tags for') + ' ' + str(tags['name:'+str(user_config['lang'])]) + '\n\n'
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
    bot.sendMessage(m)


def MapCommand(message, chat_id, user_id, user, zoom=None, imgformat='png', lat=None, lon=None):
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
                bot.sendDocument(chat_id, data, 'map.pdf')
            elif imgformat == 'jpeg':
                bot.sendPhoto(chat_id, data, 'map.jpg', '©' + _('OSM contributors'))
            elif imgformat == 'png':
                bot.sendPhoto(chat_id, data, 'map.png', '©' + _('OSM contributors'))
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
                    bot.sendDocument(chat_id, data, 'map.pdf')
                elif imgformat == 'jpeg':
                    bot.sendPhoto(
                        chat_id, data, 'map.jpg', '©' + _('OSM contributors'))
                elif imgformat == 'png':
                    bot.sendPhoto(
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
                        bot.sendDocument(chat_id, data, 'map.pdf')
                    elif imgformat == 'jpeg':
                        bot.sendPhoto(
                            chat_id, data, 'map.jpg', '©' + _('OSM contributors'))
                    elif imgformat == 'png':
                        bot.sendPhoto(
                            chat_id, data, 'map.png', '©' + _('OSM contributors'))
            else:
                text = get_template('cant_understand_message.md').render()
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
                    bot.sendPhoto(chat_id, data, 'map.png', '©' + _('OSM contributors'))
            else:
                text = get_template('cant_understand_message.md').render()
                m = Message(chat_id,text)
                response.append(m)
    bot.sendMessage(response)


def PhoneCommand(message, chat_id):
    id = message[9:]
    element_type = message[6: 9]
    osm_data = getData(id, element_type)
    if 'phone' in osm_data['tag']:
        template = get_template('phone_message.md')
        text = template.render(phone=osm_data['tag']['phone'])
        m = Message(chat_id, text)
        bot.sendMessage(m)
    if 'contact:phone' in osm_data['tag']:
        template = get_template('phone_message.md')
        text = template.render(phone=osm_data['tag']['contact:phone'])
        m = Message(chat_id, text)
        bot.sendMessage(m)


def CleanMessage(message):
    if message.startswith('@osmbot'):
        message = message[8:]
    message = message.replace('\n', '').replace('\r', '')
    return message


def DetailsCommand(message, user_config, chat_id):
    preview = False
    result = re.match('/details\s*(?P<type>nod|way|rel)\s*(?P<id>\d*)', message)
    if not result:
        text = get_template('not_found_id_message.md').render()
        m = Message(
            chat_id,
            text,
            disable_web_page_preview=(not preview)
        )
        bot.sendMessage(m)
        return None
    params = result.groupdict()
    element_type = params['type']
    identifier = params['id']
    if element_type in ['nod', 'way', 'rel']:
        osm_data = getData(identifier, geom_type=element_type)
    else:
        osm_data = getData(identifier)
    if osm_data is None:
        text = get_template('not_found_id_message.md').render()
        m = Message(
            chat_id,
            text,
            disable_web_page_preview=(not preview)
        )
        bot.sendMessage(m)
    else:
        if osm_data['tag'] == {}:
            text = get_template('not_recognized_message.md').render()
            m = Message(chat_id, text)
            bot.sendMessage(m)
        else:
            preview = False
            if 'website' in osm_data['tag'] or 'wikidata' in osm_data['tag'] or 'wikipedia' in osm_data['tag']:
                preview = True
            text = get_template('details_message.md').render(data=osm_data, type=element_type, identifier=identifier, user_config=user_config)
            m = Message(chat_id, text, disable_web_page_preview=(not preview), parse_mode='Markdown')
            bot.sendMessage(m)

def NearestCommand(message, chat_id, user_id, user, config=None, lat=None, lon=None, type=None, distance=None):
    if lat is not None and lon is not None:
        api = overpass.API()
        query = type_query[type.encode('unicode_escape')]['query']

        bbox = 'around:{0},{1},{2}'.format(distance, lat, lon)
        current_app.logger.debug('bbox:{}'.format(bbox))
        query = query.format(bbox)
        query = '({});out body center;'.format(query)
        current_app.logger.debug('query:{}'.format(query))
        data = api.Get(query.format(bbox))

        user.set_field(user_id, 'mode', 'normal')
        pretty_tags(data, chat_id, type, config, chat_id, lat=lat, lon=lon, link=True)

    else:
        t = message.replace('/nearest', '').strip().split(' ')[0]
        if t.encode('unicode_escape') not in type_query:
            text = get_template('not_implemented_message.md').render()
            m = Message(chat_id, text)
            bot.sendMessage(m)

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
        text = get_template('send_location_message.md').render()
        m = Message(chat_id, text)
        bot.sendMessage(m)


def RawCommand(message, chat_id):
    type = message[4:7]
    if type == 'nod' or type == 'way' or type == 'rel':
        identificador = message[7:]
        osm_data = getData(identificador, geom_type=type)
    else:
        identificador = message[7:].strip()
        osm_data = getData(identificador)
    if osm_data is None:
        text = get_template('not_found_id_message.md').render()
        m = Message(chat_id, text)
        bot.sendMessage(m)
    else:
        if osm_data['tag'] == {}:
            m = Message(
                chat_id,
                _("Sorry, but now I can't recognize tags for this element, perhaps with my new features I will do it") +
                ' \xF0\x9F\x98\x8B'
            )
            bot.sendMessage(m)
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
                t += "{0} = {1}\n".format(tag,osm_data['tag'][tag])
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
            bot.sendMessage(response)


def get_template(template_name):
    url = os.path.join('bot/templates', template_name)
    with open(url) as f:
        template_text = f.read()
    return jinja_env.from_string(template_text)


def answer_inline(message, query, chat_id, user_id, user_config, is_group, user):
    nom = pynominatim.Nominatim()
    search_results = nom.query(message)
    temp = get_template('inline_article.md')
    inline_query_id = query['inline_query']['id']
    results = []
    for index, r in enumerate(search_results[:10]):
        #text = temp.render(data=r)
        element_type = ''
        if r['osm_type'] == 'node':
            element_type = 'nod'
        elif r['osm_type'] == 'way':
            element_type = 'way'
        elif r['osm_type'] == 'relation':
            element_type = 'rel'
        osm_data = getData(r['osm_id'], geom_type=element_type)
        params = {'data': osm_data, 'type': element_type,
                  'identifier': r['osm_id'], 'user_config': user_config}
        text = temp.render(**params)
        answer = InputTextMessageContent(text, 'Markdown')
        result = InlineQueryResultArticle('article', '{}/{}'.format(inline_query_id, index), title=r['display_name'], input_message_content=answer)
        results.append(result)
    bot.answerInlineQuery(inline_query_id, results, is_personal=False, cache_time=86400)


def answer_message(message, query, chat_id, user_id, user_config, is_group, user,message_type):
    if message_type == 'inline':
        answer_inline(message, query, chat_id, user_id, user_config, is_group, user)
    else:
        preview = False
        response = []
        if message.lower() == '/start':
            user.set_field(chat_id, 'mode', 'normal')
            text = get_template('start_answer.md').render()
            m = Message(
                chat_id, text,
                disable_web_page_preview=(not preview),
                parse_mode='Markdown')
            bot.sendMessage(m)
        elif 'location' in query['message']:
            if user_config is not None and 'mode' in user_config and user_config['mode'] == 'map':
                MapCommand(
                    message, chat_id, user_id, user, zoom=user_config["zoom"],
                    imgformat=user_config['format'],
                    lat=float(query['message']['location']['latitude']),
                    lon=float(query['message']['location']['longitude']))
            elif user_config.get('mode', None) == 'nearest':
                NearestCommand(
                    message, chat_id, user_id, user,
                    lat=float(query['message']['location']['latitude']),
                    lon=float(query['message']['location']['longitude']),
                    distance=user_config['distance'],
                    type=user_config['type'],
                    config=user_config
                )
        elif user_config['mode'] == 'settings':
            if message == 'Language':
                response += LanguageCommand(message, user_id, chat_id, user,
                                            is_group)
            elif message == 'Answer only when mention?':
                AnswerCommand(message, user_id, chat_id, user)
            else:
                text = get_template('seting_not_recognized_message.md').render()
                m = Message(
                    chat_id,
                    text,
                    disable_web_page_preview=(not preview),
                    parse_mode='Markdown'
                )
                bot.sendMessage(m)
                user.set_field(chat_id, 'mode', 'normal', group=is_group)
        elif user_config['mode'] == 'setlanguage':
            response += SetLanguageCommand(message, user_id, chat_id, user,
                                           is_group)
        elif user_config['mode'] == 'setonlymention':
            response += SetOnlyMention(message, user_id, chat_id, user, is_group)
        elif 'text' in query['message']:
            if re.match(".*geo:-?\d+(\.\d*)?,-?\d+(\.\d*)?", message) is not None and "mode" in user_config and user_config['mode'] == 'map':
                m = re.match(
                    ".*geo:(?P<lat>-?\d+(\.\d*)?),(?P<lon>-?\d+(\.\d*)?).*",
                    message)
                lat = m.groupdict()['lat']
                lon = m.groupdict()['lon']
                response += MapCommand(
                    message, chat_id, user_id, user,
                    zoom=user_config['zoom'],
                    imgformat=user_config['format'],
                    lat=float(lat), lon=float(lon))
            elif message == 'Language':
                response += LanguageCommand(message, user_id, chat_id, user,
                                            is_group)
            elif message == 'Answer only when mention?':
                response += AnswerCommand(message, user_id, chat_id, user)
            elif message.lower().startswith('/settings'):
                SettingsCommand(message, user_id, chat_id, user, is_group)
            elif message.lower().startswith('/nearest'):
                NearestCommand(message, chat_id, user_id, user)
            elif message.lower().startswith('/map'):
                MapCommand(message, chat_id, user_id, user)
            elif re.match('/phone.*', message.lower()):
                PhoneCommand(message, chat_id)
            elif re.match('/details.*', message.lower()):
                try:
                    DetailsCommand(message, user_config, chat_id)
                except Exception as e:
                    print e.message
            elif re.match("/raw.*", message.lower()):
                try:
                    RawCommand(message, chat_id)
                except Exception as e:
                    current_app.logger.debug(e.message)
                    import traceback
                    current_app.logger.debug(traceback.format_exc())
                    pass
            elif message.lower().startswith('/legend'):
                LegendCommand(message, chat_id)
            elif message.lower().startswith('/about'):
                text = get_template('about_answer.md').render()
                m = Message(
                    chat_id, text,
                    disable_web_page_preview=(not preview),
                    parse_mode='Markdown')
                bot.sendMessage(m)
            elif message.lower().startswith('/help'):
                text = get_template('help_message.md').render()
                response = [text]
                response[-1] = response[-1].replace('_', '\_')
            elif re.match('/search.*', message.lower()) is not None and message[8:] != '':
                SearchCommand(message, user_config, chat_id)
            elif re.match('/search', message.lower()) is not None:
                m = Message(
                    chat_id,
                    _('Please indicate what are you searching with command /search <search_term>')
                )
                bot.sendMessage(m)
            else:
                m = Message(
                    chat_id,
                    _('Use /search <search_term> command to indicate what you are searching')
                )
                bot.sendMessage(m)
        if response:
            m = Message(chat_id, response,
                disable_web_page_preview=(not preview),
                parse_mode='Markdown'
            )
            bot.sendMessage(m)


@osmbot.route('/hook/<string:token>', methods=['POST'])
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
                message_type = 'query'
                if 'from' in query['message'] and 'id' in query['message']['from']:
                    is_group = query['message']['chat']['type'] == u'group'
                    if is_group:
                        identifier = query['message']['chat']['id']
                    else:
                        identifier = query['message']['from']['id']
                    user_config = user.get_user(identifier, group=is_group)
                    user_id = query['message']['from']['id']
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

                if is_group and (not user_config['onlymentions'] and user_config['onlymentions'] is not None )and not '@osmbot' in message.lower():
                    if message != 'Yes' and message != 'No' and message != 'Language' and message != 'Answer only when mention?' and message not in avaible_languages.keys():
                        return 'OK'
                else:
                    message = message.replace('@osmbot', '')
                    message = message.replace('@OSMbot', '')
            lang = gettext.translation('messages', localedir='./bot/locales/', languages=[user_config['lang'], 'en'])
            lang.install()
            jinja_env.install_gettext_translations(gettext.translation('messages', localedir='./bot/locales/', languages=[user_config['lang'], 'en']))
            _ = lang.gettext

            message = CleanMessage(message)
            answer_message(message, query, chat_id, user_id, user_config, is_group, user,message_type)
        except Exception as e:
            print str(e)
            import traceback
            traceback.print_exc()
            current_app.sentry.captureException()

            lang = gettext.translation('messages', localedir='./bot/locales/', languages=[user_config['lang'], 'en'])
            lang.install()
            _ = lang.gettext
            text = get_template('error_message.md').render()
            m = Message(chat_id, text)
            bot.sendMessage(m)
        config['last_id'] = query['update_id']
        config.write()
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
