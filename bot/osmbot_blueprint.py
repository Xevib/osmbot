# -*- coding: utf-8 -*-
from flask import Flask
from flask import request, current_app, Blueprint
import re
import nominatim
import sched, time
from osmapi import OsmApi
from bot import OSMbot
import urllib
from configobj import ConfigObj
from typeemoji import typeemoji
from maptools import download, genBBOX
import gettext




import user as u
avaible_languages = ['Catalan', 'English', 'Spanish', 'Swedish']

application = Flask(__name__)
application.debug = True
config = ConfigObj("bot.conf")
token = config["token"]
user = u.User("osmbot.db")
bot = OSMbot(token)
api = OsmApi()
nom = nominatim.Nominatim()

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
    elif geom_type == "nod":
        osm_data = api.NodeGet(int(id))
    elif geom_type == "way":
            osm_data = api.WayGet(int(id))
    elif geom_type == "rel":
        osm_data = api.RelationGet(int(id))
    return osm_data

def SetLanguageCommand(message,user_id,chat_id,u):
    if message in avaible_languages:
        if message == 'Catalan':
            u.set_field(user_id, 'lang', 'ca')
        elif message == 'English':
            u.set_field(user_id, 'lang', 'en')
        elif message == 'Spanish':
            u.set_field(user_id, 'lang', 'es')
        elif message == 'Swedish':
            u.set_field(user_id, 'lang', 'sv')
        u.set_field(user_id, 'mode', 'normal')
        bot.sendMessage(chat_id, _("Now I will talk you with the new language") +
                        ' \xF0\x9F\x98\x99'+'\xF0\x9F\x92\xAC', reply_markup={'hide_keyboard': True})
        return []
    else:
        u.set_field(user_id, 'mode', 'normal')

        bot.sendMessage(chat_id,
                        _("Ooops! I can't talk this language") + ' \xF0\x9F\x98\xB7 (' + _("yet") +
                        ' \xF0\x9F\x98\x89)\n' + _("But you can help me to learn it in Transifex") +
                        ' \xF0\x9F\x8E\x93\nhttps://www.transifex.com/osm-catala/osmbot/',
                        reply_markup={'hide_keyboard': True})
        return []

def LanguageCommand(message, user_id, chat_id, user):
    keyboard = []
    for lang in avaible_languages:
        keyboard.append([lang])
    bot.sendMessage(chat_id, _("Choose the language for talk with you") +
                    ' \xF0\x9F\x98\x8F', reply_markup={'keyboard':keyboard, 'one_time_keyboard': True})
    user.set_field(user_id, 'mode', 'setlanguage')
    return []

def SettingsCommand(message,user_id,chat_id,u):
    bot.sendMessage(chat_id, _("What do you want to configure?") +
                    ' \xF0\x9F\x91\x86', reply_markup={'keyboard': [['Language']], 'one_time_keyboard': True})
    u.set_field(user_id, 'mode', 'settings')
    return []

def LegendCommand(message):
    t = ""
    filt = message[8:]
    selected_keys = []
    for key in typeemoji.keys():
        if filt in key:
            selected_keys.append(key)
    selected_keys = sorted(selected_keys)
    for key in selected_keys:
        t += typeemoji[key]+" "+key+"\n"
    if len(selected_keys)>50:
        return [t, _("If you see strange emojis it's due a Telegram easter egg")]
    elif len(selected_keys) == 0:
        return [_('No emoji found, perhaps you should try with /legend <osm_key:value>')]
    return t

def SearchCommand(message,user_config):
    response = []
    t = ""
    search = message[8:].replace("\n", "").replace("\r", "")
    results = nom.query(search, acceptlanguage=user_config['lang'])
    if len(results) == 0:
        response = [_('Sorry but I couldn\'t find any result for "{0}"').format(search)+" \xF0\x9F\x98\xA2\n" +
                    _('But you can try to improve OpenStreetMap')+'\xF0\x9F\x94\x8D\nhttp://www.openstreetmap.org']
    else:
        t = _("Results for")+' "{0}":\n\n'.format(search)
        for result in results:
            if 'osm_id' in result:
                try:
                    osm_data = getData(result['osm_id'])
                except:
                    osm_data = None
            else:
                osm_data = None
            type = result['class']+":"+result['type']
            if type in typeemoji:
                t += typeemoji[result['class'] + ":" + result['type']] + " " + result["display_name"] + "\n"
            else:
                t += "\xE2\x96\xB6 "+result["display_name"]+"\n"
            t += "\xF0\x9F\x93\x8D http://www.openstreetmap.org/?minlat={0}&maxlat={1}&minlon={2}&maxlon={3}&mlat={4}&mlon={5}\n\n".format(result['boundingbox'][0],result['boundingbox'][1],result['boundingbox'][2],result['boundingbox'][3],result['lat'],result['lon'])
            if osm_data is not None and ('phone' in osm_data['tag'] or 'contact:phone' in osm_data['tag']):
                t += "\n" + _("More info") + " /details{0}".format(result['osm_id']) + "\n" + _("Phone") + " /phone{0}".format(result['osm_id']) + "\n\n"
            else:
                if 'osm_id' in result:
                    if 'osm_type' in result and result['osm_type'] =="node":
                        t += "\n" + _("More info") + " /detailsnod{0}\n\n".format(result['osm_id'])
                    elif 'osm_type' in result and result['osm_type'] == "way":
                        t += "\n"+_("More info")+" /detailsway{0}\n\n".format(result['osm_id'])
                    elif 'osm_type' in result and result['osm_type'] =="relation":
                        t += "\n" + _("More info") + " /detailsrel{0}\n\n".format(result['osm_id'])
                    else:
                        t += "\n" + _("More info") + " /details{0}\n\n".format(result['osm_id'])

        t += "\xC2\xA9" + _("OpenStreetMap contributors") + "\n"
    return response + [t]

def pretty_tags(data):
    preview = False
    tags = data['tag']
    response = []
    t = ""
    if 'name' in tags:
        t = "\xE2\x84\xB9 " + _("Tags for ")+str(tags['name']) + "\n"
    if 'addr:housenumber' in tags or 'addr:street' in tags or 'addr:city' in tags or 'addr:country' in tags:
        t += "\n"
    if 'addr:housenumber' and 'addr:street' in tags:
        t += "\xF0\x9F\x93\xAE "+tags['addr:street']+", "+tags['addr:housenumber']+"\n"
    else:
        if 'addr:housenumber' in tags:
            t += "\xF0\x9F\x93\xAE "+tags['addr:housenumber']+"\n"
        if 'addr:street' in tags:
            t += "\xF0\x9F\x93\xAE "+tags['addr:street']+"\n"
    if 'addr:city' in tags:
        t += tags['addr:city'] + "\n"
    if 'addr:country' in tags:
       t += tags['addr:country'] + "\n"
    if 'phone' in tags:
        t += "\xF0\x9F\x93\x9E " + str(tags['phone']) + "\n"
    if 'contact:phone' in tags:
        t += "\xF0\x9F\x93\x9E " + str(tags['contact:phone']) + "\n"
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
        t += "\xF0\x9F\x91\xAA " + str(tags['population']) + "\n"
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
    t += "\n\xC2\xA9 " + _("OpenStreetMap contributors") + "\n"

    response.append(t)
    return (preview,response)

def MapCommand(message, chat_id, user_id,zoom=None,imgformat=None,lat=None,lon=None):
    response = []
    message = message[4:]
    if lat is not None and lon is not None:
        bbox = genBBOX(lat, lon, 0.1)
        try:
            data = download(bbox, imageformat=imgformat, zoom=zoom)
        except ValueError as v:
            response.append(v.message)
        else:
            if imgformat == 'pdf':
                bot.sendDocument(chat_id, data, 'map.pdf')
            elif imgformat == 'jpeg':
                bot.sendPhoto(chat_id, data, "map.jpg", "Map")
            elif imgformat == 'png':
                bot.sendPhoto(chat_id, data, "map.png", "Map")
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
            lat = float(m.groupdict()["lat"])
            lon = float(m.groupdict()["lon"])
            imgformat = m.groupdict()["imgformat"]
            zoom = m.groupdict()["zoom"]
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
                    bot.sendPhoto(chat_id, data, "map.jpg", "Map")
                elif imgformat == 'png':
                    bot.sendPhoto(chat_id, data, "map.png", "Map")
        elif re.match(" -?\d+(\.\d*)?,-?\d+(\.\d*)?,-?\d+(\.\d*)?,-?\d+(\.\d*)? ?(png|jpeg|pdf)? ?\d{0,2}",message):
            m = re.match(" (?P<bb1>-?\d+(\.\d*)?),(?P<bb2>-?\d+(\.\d*)?),(?P<bb3>-?\d+(\.\d*)?),(?P<bb4>-?\d+(\.\d*)?) ?(?P<format>png|jpg|pdf)? ?(?P<zoom>\d{0,2})",message)
            if m is not None:
                bbox1 = m.groupdict()["bb1"]
                bbox2 = m.groupdict()["bb2"]
                bbox3 = m.groupdict()["bb3"]
                bbox4 = m.groupdict()["bb4"]
                imgformat = m.groupdict()["format"]
                zoom = m.groupdict()["zoom"]
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
                        bot.sendPhoto(chat_id, data, "map.jpg", "Map")
                    elif imgformat == 'png':
                        bot.sendPhoto(chat_id, data, "map.png", "Map")
            else:
                response.append(_("Sorry, I can't understand you")+" \xF0\x9F\x98\xB5\n" +
                                _("Perhaps I could help you with the command /help") + " \xF0\x9F\x91\x8D")
        else:
            response.append(_("Sorry, I can't understand you") + " \xF0\x9F\x98\xB5\n" +
                            _("Perhaps I could help you with the command /help") + " \xF0\x9F\x91\x8D")
    return response

def PhoneCommand(message):
    id = message[6:]
    osm_data = getData(id)
    if "phone" in osm_data["tag"]:
        response = ["\xF0\x9F\x93\x9E " + osm_data["tag"]["phone"]]
    if "contact:phone" in osm_data["tag"]:
        response = ["\xF0\x9F\x93\x9E " + osm_data["tag"]["contact:phone"]]
    return response

def CleanMessage(message):
    if message.startswith("@osmbot"):
        message = message[8:]
    message = message.replace("\n", "").replace("\r", "")
    return message

def DetailsCommand(message):
    preview = False
    response =[]
    t = ""
    type = message[8:11]
    if type == "nod" or type == "way" or type == "rel":
        id = message[11:]
        osm_data = getData(id, geom_type=type)
    else:
        id = message[8:].strip()
        osm_data = getData(id)
    if osm_data is None:
        response.append(_("Sorry but I couldn't find any result, please check the ID"))
    else:
        if osm_data["tag"] == {}:
            response = [_("Sorry, but now I can't recognize tags for this element, perhaps with my new features I will do it") +
                        " \xF0\x9F\x98\x8B"]
        else:
            response.append(t)
            t = ""
            (preview, message) = pretty_tags(osm_data)
            response.append(message)
    return (preview, response)

@osmbot.route("/hook/<string:token>", methods=["POST"])
def attend_webhook(token):
    current_app.logger.debug("token:%s", token)
    if token == config['token']:
        return "OK"
    else:
        return "NOT ALLOWED"

if __name__ == "__main__":

    application.run(host='0.0.0.0')