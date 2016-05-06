# -*- coding: utf-8 -*-
import re
import math
from flask import Flask
from flask import request, current_app, Blueprint
import pynominatim
from osmapi import OsmApi
from bot import OSMbot
import urllib
from configobj import ConfigObj
from typeemoji import typeemoji
from maptools import download, genBBOX, getScale
import gettext
import overpass
from overpass_query import type_query
import user as u


avaible_languages = {'Catalan': 'ca', 'English': 'en', 'Spanish': 'es', 'Swedish': 'sv', 'Asturian': 'ast',
                     'Galician': 'gl', 'French': 'fr', 'Italian': 'it', 'Basque': 'eu', 'Polish': 'pl',
                     'German': 'de'}

application = Flask(__name__)
application.debug = True
config = ConfigObj('bot.conf')

token = config['token']
user = u.User(config['host'], config['database'], config['user'], config['password'])
bot = OSMbot(token)
api = OsmApi()
nom = pynominatim.Nominatim()

osmbot = Blueprint(
    'osmbot', __name__,
    template_folder='templates',
    static_folder='static'
)


def getData(id, geom_type=None):
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
        bot.sendMessage(chat_id, _('Now I only will answer when mention'), reply_markup={'hide_keyboard': True})
    else:
        bot.sendMessage(chat_id, _('Now I allways will answer') +' \xF0\x9F\x98\x99'+'\xF0\x9F\x92\xAC',
                        reply_markup={'hide_keyboard': True})
    return []


def SetLanguageCommand(message, user_id, chat_id, u, group=False):
    if message in avaible_languages:
        if group:
            u.set_field(chat_id, 'lang', avaible_languages[message],group=group)
            u.set_field(chat_id, 'mode', 'normal', group=group)
        else:
            u.set_field(user_id, 'lang', avaible_languages[message],group=group)
            u.set_field(user_id, 'mode', 'normal', group=group)
        bot.sendMessage(chat_id, _('Now I will talk you with the new language') +
                        ' \xF0\x9F\x98\x99'+'\xF0\x9F\x92\xAC', reply_markup={'hide_keyboard': True})
        return []
    else:
        if group:
            u.set_field(chat_id, 'mode', 'normal')
        else:
            u.set_field(user_id, 'mode', 'normal')
        bot.sendMessage(chat_id,
                        _("Ooops! I can't talk this language") + ' \xF0\x9F\x98\xB7 (' + _('yet') +
                        ' \xF0\x9F\x98\x89)\n' + _('But you can help me to learn it in Transifex') +
                        ' \xF0\x9F\x8E\x93\nhttps://www.transifex.com/osm-catala/osmbot/',
                        reply_markup={'hide_keyboard': True})
        return []


def AnswerCommand(message, user_id, chat_id, user):
    bot.sendMessage(chat_id, _('Should I answer without a mention?') +
                    ' \xF0\x9F\x98\x8F', reply_markup={'keyboard': [['Yes'], ['No']], 'one_time_keyboard': True})
    user.set_field(chat_id, 'mode', 'setonlymention', group=True)
    return []

def LanguageCommand(message, user_id, chat_id, user, group=False):
    keyboard = []
    for lang in sorted(avaible_languages.keys()):
        keyboard.append([lang])
    bot.sendMessage(chat_id, _('Choose the language for talk with you') +
                    ' \xF0\x9F\x98\x8F', reply_markup={'keyboard': keyboard, 'one_time_keyboard': True})
    if group:
        user.set_field(chat_id, 'mode', 'setlanguage', group=group)
    else:
        user.set_field(user_id, 'mode', 'setlanguage', group=group)
    return []

def SettingsCommand(message, user_id, chat_id, u, group=False):
    buttons = [['Language']]
    if group:
        buttons.append(['Answer only when mention?'])
    bot.sendMessage(chat_id, _('What do you want to configure?') +
                    ' \xF0\x9F\x91\x86', reply_markup={'keyboard': buttons, 'one_time_keyboard': True})
    if group:
        u.set_field(chat_id, 'mode', 'settings', group=group)
    else:
        u.set_field(user_id, 'mode', 'settings', group=group)
    return []


def LegendCommand(message):
    t = ''
    filt = message[8:]
    selected_keys = []
    for key in typeemoji.keys():
        if filt in key:
            selected_keys.append(key)
    selected_keys = sorted(selected_keys)
    for key in selected_keys:
        t += typeemoji[key]+' ' + key+'\n'
    if len(selected_keys) > 50:
        return [t, _("If you see strange emojis it's due a Telegram easter egg")]
    elif len(selected_keys) == 0:
        return [_('No emoji found, perhaps you should try with /legend <osm_key:value>')]
    return t


def SearchCommand(message, user_config):
    import pynominatim

    response = []
    t = ''
    search = message[8:].replace('\n', '').replace('\r', '')
    nom = pynominatim.Nominatim()
    results = nom.query(search)
    if not results:
        response = [_('Sorry but I couldn\'t find any result for "{0}"').format(search) + " \xF0\x9F\x98\xA2\n" +
                    _('But you can try to improve OpenStreetMap') + '\xF0\x9F\x94\x8D\nhttp://www.openstreetmap.org']
    else:
        t = _('Results for') + ' "{0}":\n\n'.format(search)
        for result in results[:10]:
            if 'osm_id' in result:
                try:
                    osm_data = getData(result['osm_id'])
                except:
                    osm_data = None
            else:
                osm_data = None
            type = result['class'] + ':' + result['type']
            if type in typeemoji:
                t += typeemoji[result['class'] + ':' + result['type']] + " " + result['display_name'] + '\n'
            else:
                t += '\xE2\x96\xB6 ' + result['display_name']+'\n'
            t += '\xF0\x9F\x93\x8D http://www.openstreetmap.org/?minlat={0}&maxlat={1}&minlon={2}&maxlon={3}&mlat={4}&mlon={5}\n'.format(result['boundingbox'][0],result['boundingbox'][1],result['boundingbox'][2],result['boundingbox'][3],result['lat'],result['lon'])
            if osm_data is not None and ('phone' in osm_data['tag'] or 'contact:phone' in osm_data['tag']):
                if 'osm_type' in result and result['osm_type'] == 'node':
                    t += _('More info') + ' /detailsnod{0}\n'.format(result['osm_id'])
                elif 'osm_type' in result and result['osm_type'] == 'way':
                    t += _('More info')+' /detailsway{0}\n'.format(result['osm_id'])
                elif 'osm_type' in result and result['osm_type'] == 'relation':
                    t += _('More info') + ' /detailsrel{0}\n'.format(result['osm_id'])
                else:
                    t += '\n' + _('More info') + ' /details{0}'.format(result['osm_id'])
                t += _("Phone") + " /phone{0}".format(result['osm_id']) + "\n\n"
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
    return response + [t]


def pretty_tags(data, identificador, type, user_config, lat=None, lon=None, link=False):
    response = []
    preview = False
    if 'tag' in data:
        tags = data['tag']
    elif 'elements' in data:
        tags = data['elements']
        min_dist =None
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
            response.append(_('No element found'))
            preview = False
            return preview, response
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
        t += "\xF0\x9F\x8C\x8D " + _('European country') + "\n"
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

    response.append(t)
    return preview, response


def MapCommand(message, chat_id, user_id, user, zoom=None, imgformat='png', lat=None, lon=None):
    response = []
    message = message[4:]
    if lat is not None and lon is not None:
        bbox = genBBOX(lat, lon, 0.1)
        try:
            data = download(bbox, _, imageformat=imgformat, zoom=zoom)
        except ValueError as v:
            response.append(v.message)
        else:
            if imgformat == 'pdf':
                bot.sendDocument(chat_id, data, 'map.pdf')
            elif imgformat == 'jpeg':
                bot.sendPhoto(chat_id, data, "map.jpg", "©OSM contributors")
            elif imgformat == 'png':
                bot.sendPhoto(chat_id, data, "map.png", "©OSM contributors")
        user.set_field(user_id, 'mode', 'normal')
    else:
        if re.match(" ?(png|jpg|pdf)? ?(\d?\d)?$", message):
            m = re.match(" ?(?P<imgformat>png|jpg|pdf)? ?(?P<zoom>\d{0,2})$",message)
            zoom = m.groupdict()["zoom"]
            imgformat = m.groupdict()["imgformat"]
            response.append(_("Please send me your location") + " \xF0\x9F\x93\x8D " +
                            _("to receive the map.") + ".\n" +
                            _("You can do it with the Telegram paperclip button") + " \xF0\x9F\x93\x8E.")
            if imgformat is None:
                imgformat = 'png'
            if zoom == '':
                zoom = 19
            user.set_field(user_id, 'format', imgformat)
            user.set_field(user_id, 'zoom', zoom)
            user.set_field(user_id, 'mode', 'map')

        elif re.match(" -?\d+(\.\d*)?,-?\d+(\.\d*)? (pngjpg|pdf)? ?(\d?\d)?", message):
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
                data = download(bbox, imageformat=imgformat, zoom=zoom)
            except ValueError as v:
                response.append(v.message)
            else:
                if imgformat == 'pdf':
                    bot.sendDocument(chat_id, data, 'map.pdf')
                elif imgformat == 'jpeg':
                    bot.sendPhoto(chat_id, data, 'map.jpg', '©OSM contributors')
                elif imgformat == 'png':
                    bot.sendPhoto(chat_id, data, 'map.png', '©OSM contributors')
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
                    data = download([bbox1, bbox2, bbox3, bbox4], imgformat, zoom=zoom)
                except ValueError as v:
                    response.append(v.message)
                else:
                    if imgformat == 'pdf':
                        bot.sendDocument(chat_id, data, 'map.pdf')
                    elif imgformat == 'jpeg':
                        bot.sendPhoto(chat_id, data, 'map.jpg', '©OSM contributors')
                    elif imgformat == 'png':
                        bot.sendPhoto(chat_id, data, 'map.png', '©OSM contributors')
            else:
                response.append(_("Sorry, I can't understand you")+" \xF0\x9F\x98\xB5\n" +
                                _("Perhaps I could help you with the command /help") + " \xF0\x9F\x91\x8D")
        else:
            res = nom.query(message)
            if res:
                bbox = res[0]['boundingbox']
                auto_scale = getScale([bbox[0],bbox[2],bbox[1],bbox[3]])
                try:
                    data = download([bbox[2],bbox[0],bbox[3],bbox[1]], _, scale=auto_scale )
                except ValueError as v:
                    response.append(v.message)
                else:
                    bot.sendPhoto(chat_id, data, 'map.png', '©OSM contributors')
            else:
                response.append(_("Sorry, I can't understand you") + ' \xF0\x9F\x98\xB5\n' +
                                _('Perhaps I could help you with the command /help') + ' \xF0\x9F\x91\x8D')
    return response


def PhoneCommand(message):
    id = message[6:]
    osm_data = getData(id)
    if 'phone' in osm_data['tag']:
        return ['\xF0\x9F\x93\x9E {}'.format(osm_data['tag']['phone'])]
    if 'contact:phone' in osm_data['tag']:
        return ['\xF0\x9F\x93\x9E {}'.format(osm_data["tag"]["contact:phone"])]
    return []


def CleanMessage(message):
    if message.startswith('@osmbot'):
        message = message[8:]
    message = message.replace('\n', '').replace('\r', '')
    return message


def DetailsCommand(message, user_config):
    preview = False
    response = []
    t = ''
    params = re.match('/details\s*(?P<type>nod|way|rel)\s*(?P<id>\d*)', message).groupdict()
    element_type = params['type']
    identifier = params['id']
    if element_type in ['nod', 'way', 'rel']:
        osm_data = getData(identifier, geom_type=element_type)
    else:
        osm_data = getData(identifier)
    if osm_data is None:
        response.append(_("Sorry but I couldn't find any result, please check the ID"))
    else:
        if osm_data['tag'] == {}:
            response = [_("Sorry, but now I can't recognize tags for this element, perhaps with my new features I will do it") +
                        ' \xF0\x9F\x98\x8B']
        else:
            response.append(t)
            t = ''
            (preview, message) = pretty_tags(osm_data, identifier, element_type, user_config)
            response.append(message)
    return preview, response


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

        return pretty_tags(data, chat_id, type, config, lat=lat, lon=lon, link=True)
    else:
        t = message.replace('/nearest', '').strip().split(' ')[0]
        if t.encode('unicode_escape') not in type_query:
            return ['', _('Sorry but this query it\'s not implemented yet')]

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
        return [ _('Please send me your location') + ' \xF0\x9F\x93\x8D ' +
                        _('and I\'ll send you the nearest element') + '.\n' +
                        _('You can do it with the Telegram paperclip button') + ' \xF0\x9F\x93\x8E.']


def RawCommand(message):
    preview = False
    response = []
    t = ''
    type = message[4:7]
    if type == "nod" or type == "way" or type == "rel":
        identificador = message[7:]
        osm_data = getData(identificador, geom_type=type)
    else:
        identificador = message[7:].strip()
        osm_data = getData(identificador)
    if osm_data is None:
        response.append(_("Sorry but I couldn't find any result, please check the ID"))
    else:
        if osm_data["tag"] == {}:
            response = [_("Sorry, but now I can't recognize tags for this element, perhaps with my new features I will do it") +
                        " \xF0\x9F\x98\x8B"]
        else:
            response.append(t)
            preview = False
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
                    response.append(t)
                    i = 0
                    parts += 1
                    if 'name' in osm_data['tag']:
                        t = '\xE2\x9C\x8F '+_('Raw data for')+' {0} ({1}/{2})\n\n'.format(osm_data['tag']['name'], parts, max_parts)
                    else:
                        t = '\xE2\x9C\x8F '+_('Raw data') + '({0}/{1})\n\n'.format(parts, max_parts)
            t += '\n\xC2\xA9 ' + _('OpenStreetMap contributors')
            response.append(t)
    return preview, response


@osmbot.route("/hook/<string:token>", methods=["POST"])
def attend_webhook(token):
    user = u.User(config['host'], config['database'], config['user'], config['password'])
    current_app.logger.debug("token:%s", token)
    if token == config['token']:
        try:
            query = request.json
            preview = False
            response = []
            if 'from' in query['message'] and 'id' in query['message']['from']:
                is_group = query['message']['chat']['type'] == u'group'
                if is_group:
                    identifier = query['message']['chat']['id']
                else:
                    identifier = query['message']['from']['id']
                user_config = user.get_user(identifier, group=is_group)
                user_id = query['message']['from']['id']
            else:
                user_config = user.get_defaultconfig()
                user_id = 0
            if "message" in query:
                if "text" in query["message"]:
                    message = query["message"]["text"]
                else:
                    message = ""
                chat_id = query["message"]["chat"]["id"]
            lang = gettext.translation('messages', localedir='./bot/locales/', languages=[user_config['lang'], 'en'])
            lang.install()
            _ = lang.gettext

            if is_group and (not user_config['onlymentions'] and user_config['onlymentions'] is not None )and not '@osmbot' in message.lower():
                if message != 'Yes' and message!='No' and message!='Language' and message!='Answer only when mention?' and message not in avaible_languages.keys():
                    return 'OK'
            message = CleanMessage(message)
            if message.lower() == "/start":
                user.set_field(chat_id, 'mode', 'normal')
                response = [_("Hi, I'm the robot for OpenStreetMap data") + ".\n" + _("How I can help you?")]
            elif "location" in query["message"]:
                if user_config is not None and "mode" in user_config and user_config["mode"] == "map":
                    response += MapCommand(
                        message, chat_id, user_id,user, zoom=user_config["zoom"], imgformat=user_config["format"],
                        lat=float(query["message"]["location"]["latitude"]),
                        lon=float(query["message"]["location"]["longitude"]))
                elif user_config.get('mode', None) == 'nearest':
                    response += NearestCommand(
                        message, chat_id, user_id, user, lat=float(query["message"]["location"]["latitude"]),
                        lon=float(query['message']['location']['longitude']),
                        distance=user_config['distance'], type=user_config['type'], config=user_config
                    )[1]
            elif user_config['mode'] == 'settings':
                if message == 'Language':
                    response += LanguageCommand(message, user_id, chat_id, user, is_group)
                elif message == 'Answer only when mention?':
                    response += AnswerCommand(message, user_id, chat_id, user)
                else:
                    response = [_('Setting not recognized')]
                    user.set_field(chat_id, 'mode', 'normal')
            elif user_config['mode'] == 'setlanguage':
                response += SetLanguageCommand(message, user_id, chat_id, user, is_group)
            elif user_config['mode'] == 'setonlymention':
                response += SetOnlyMention(message, user_id, chat_id, user, is_group)
            elif "text" in query["message"]:
                if re.match(".*geo:-?\d+(\.\d*)?,-?\d+(\.\d*)?", message) is not None and  "mode" in user_config and user_config["mode"] == "map":
                    m = re.match(".*geo:(?P<lat>-?\d+(\.\d*)?),(?P<lon>-?\d+(\.\d*)?).*",message)
                    lat = m.groupdict()["lat"]
                    lon = m.groupdict()["lon"]
                    response += MapCommand(message, chat_id, user_id,user, zoom=user_config["zoom"],
                                           imgformat=user_config["format"], lat=float(lat), lon=float(lon))
                elif message == "Language":
                    response += LanguageCommand(message, user_id, chat_id, user, is_group)
                elif message == 'Answer only when mention?':
                    response += AnswerCommand(message, user_id, chat_id, user)
                elif message.lower().startswith("/settings"):
                    response += SettingsCommand(message, user_id, chat_id, user, is_group)
                elif message.lower().startswith("/nearest"):
                    response += NearestCommand(message, chat_id, user_id, user)
                elif message.lower().startswith("/map"):
                    response += MapCommand(message, chat_id, user_id, user)
                elif re.match("/phone.*", message.lower()):
                    response += PhoneCommand(message)
                elif re.match("/details.*", message.lower()):
                    try:
                        (preview, r) = DetailsCommand(message,user_config)
                        response += r
                    except:
                        pass
                elif re.match("/raw.*", message.lower()):
                    try:
                        (preview, r) = RawCommand(message)
                        response += r
                    except Exception as e:
                        current_app.logger.debug(e.message)
                        import traceback
                        current_app.logger.debug(traceback.format_exc())
                        pass
                elif message.lower().startswith("/legend"):
                    response = LegendCommand(message)
                elif message.lower().startswith("/about"):
                    response = [
                        _('OpenStreetMap bot info:') + '\n\n' + _('CREDITS&CODE') + "\n\xF0\x9F\x91\xA5 " +
                        _('Author:')+' '+'OSM català'+' '+_('(Catalan OpenStreetMap community)') + "\n\xF0\x9F\x94\xA7 " +
                        _("Code:") + " https://github.com/Xevib/osmbot\n\xE2\x99\xBB " +
                        _("License: GPLv3") + ", " +
                        _("http://www.gnu.org/licenses/gpl-3.0.en.html")+"\n\xF0\x9F\x92\xAC " +
                        _("Localization:") + " https://www.transifex.com/osm-catala/osmbot/" + "\n\n" +
                        _("NEWS") + "\n\xF0\x9F\x90\xA4 Twitter: https://twitter.com/osmbot_telegram\n\xF0\x9F\x93\xA2 " + _("Telegram channel:") + " https://telegram.me/OSMbot_channel\n\n" + 
                        _("RATING")+"\n\xE2\xAD\x90 "+_("Rating&reviews") +
                        ": http://storebot.me/bot/osmbot\n\xF0\x9F\x91\x8D " + _('Please rate me at') +
                        ': https://telegram.me/storebot?start=osmbot\n\n' + _('Thanks for use @OSMbot!!')]
                elif message.lower().startswith("/help"):
                    response = [
                        _('OpenStreetMap bot help:') + '\n\n' + _('You can control me by sending these commands:') +
                        '\n\n' + _('/about - Show info about OSMbot: credits&code, news and ratings&reviews') + '\n\n' +
                        _('/details<type><osm_id> - Show some tags from OSM database by ID.') + '\n' +
                        _('/raw<type><osm_id> - Show all tags from OSM database by ID in raw format.') + '\n' +
                        _('The ID is generated by /search command, but if you know an OSM ID you can try it.') +
                        '\n' + _("The type it's optional and it can be nod(node), way(way) or rel(relation). If you don't specify it, the bot will try to deduce it") +
                        '\n\n'+_("/legend <osm_key> - Show list of pairs key=value and its emoji in OSMbot. If you don't specify an <osm_key>, shows all pairs of key=value with emoji in Osmbot") +
                        '\n\n' + _('/map <coord> <format> <scale> - Send a map with different options:')+
                        '\n  ' + _("<coord> Could be a point (lat,lon) or a bounding box (minlon,minlat,maxlon,maxlat). If you don't use this option can send your location") +
                        '\n  ' + _("<format> Could be png, jpeg or pdf. If you don't use this option, the bot use png by default") +
                        '\n  ' + _("<scale> Level of zoom (1-19). If you don't use this option, the bot use 19 by default.") +
                        '\n\n' + _("/search <search_term> - Search from Nominatim in all OpenStreetMap database.") +
                        '\n\n' + _('/nearest <type> <optional meters> - Search from Overpass the element in a certain radius')

                    ]
                elif re.match('/search.*', message.lower()) is not None and message[8:] != '':
                    response += SearchCommand(message, user_config)
                elif re.match('/search', message.lower()) is not None:
                    response = [_('Please indicate what are you searching with command /search <search_term>')]
                else:
                    response = [_('Use /search <search_term> command to indicate what you are searching')]
            bot.sendMessage(chat_id, response, disable_web_page_preview=(not preview))
        except Exception as e:
            print str(e)
            import traceback
            traceback.print_exc()
            current_app.sentry.captureMessage(str(e))

            lang = gettext.translation('messages', localedir='./bot/locales/', languages=[user_config['lang'], 'en'])
            lang.install()
            _ = lang.gettext
            bot.sendMessage(chat_id, [_('Something failed') + ' \xF0\x9F\x98\xB5 ' +
                                      _('please try it latter') + ' \xE2\x8F\xB3'],
                            disable_web_page_preview=(not preview))
        config['last_id'] = query['update_id']
        config.write()
        return 'OK'
    else:
        return 'NOT ALLOWED'

if __name__ == "__main__":
    application.run(host='0.0.0.0')

gettext.gettext('OpenStreetMap bot finds any location in world from the Nominatim OSM database and can send links and maps from OSM')
gettext.gettext('OpenStreetMap bot finds any location in the world from the Nominatim OSM database')
gettext.gettext('The bot can send links and maps (jpg, png or pdf) from OSM')
gettext.gettext('Data for all the world (cities and towns, shops -with phone number, email...-, Wikipedia links, etc)')
gettext.gettext('OSMbot is multilingual and speaks *your language here*')
