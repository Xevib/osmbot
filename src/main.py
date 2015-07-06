# -*- coding: utf-8 -*-
import re
import nominatim
import os
import sched, time
from osmapi import OsmApi
from bot import OSMbot

def pretty_tags(data):
    tags = data['tag']
    response = []
    t = ""
    if 'name' in tags:
        t = "\xF0\x9F\x93\xAE "+str(tags['name'])+"\n"
    if 'addr:housenumber' in tags or 'addr:street' in tags or 'addr:city' in tags or 'addr:country' in tags:
        t += "\n"
    if 'addr:housenumber' in tags:
        t += tags['addr:housenumber']+"\n"
    if 'addr:street' in tags:
        t += tags['addr:street']+"\n"
    if 'addr:city' in tags:
        t += tags['addr:city']+"\n"
    if 'addr:country' in tags:
       t += tags['addr:country']+"\n"
    if 'phone' in tags:
        response.append(t)
        t = ""
        response.append("\xF0\x9F\x93\x9E "+str(tags['phone'])+"\n")
    if 'fax' in tags:
        t += "\xF0\x9F\x93\xA0 "+str(tags['fax'])+"\n"
    if 'email' in tags:
        t += "\xE2\x9C\x89 "+str(tags['email'])+"\n"
    if 'website' in tags:
        t += "\xF0\x9F\x8C\x8D "+str(tags['website'])+"\n"
    if 'population' in tags:
        t += "\xF0\x9F\x91\xAA "+str(tags['population'])+"\n"
    if 'wikipedia' in tags:
        if ":" in tags["wikipedia"]:
            lang=tags['wikipedia'].split(":")[0]
            term=tags['wikipedia'].split(":")[1]
            t += "\xF0\x9F\x93\x92 http://{0}.wikipedia.org/wiki/{1}".format(lang,term)+"\n"
        else:
            t += "\xF0\x9F\x93\x92 http://wikipedia.org/wiki/{0}".format(tags["wikipedia"])+"\n"

    response.append(t)
    return response

def attend(sc):
    if os.path.isfile("last.id"):
        f = open("last.id", "r")
        last_id = int(f.read())
        f.close()
        updates = bot.getUpdates(offset=last_id+1)
    else:
        updates = bot.getUpdates()
    if updates['ok']:
        print "Attending "+str(len(updates["result"]))+" "
        for query in updates['result']:
            response = []
            t = ""
            if "text" in query["message"]:
                message = query["message"]["text"]
                usr_id = query["message"]["chat"]["id"]
                if message.startswith("@osmbot"):
                    message = message[8:]
                if message == "/start":
                    response = ["Hi,how I can help you?"]
                elif message.startswith("/details"):
                    id = message[8:].strip()
                    try:
                        osm_data = api.NodeGet(int(id))
                        if osm_data is None:
                            try:
                                osm_data = api.WayGet(int(id))
                            except:
                                osm_data = api.RelationGet(int(id))
                    except:
                        osm_data = None
                    if osm_data["tag"] == {}:
                        response = ["Sorry but this element doesn't have tags"]
                    if osm_data is None:
                        response.append('Sorry but I couldn\'t find any result,check the id')
                    else:
                        response.append(t)
                        t = ""
                        messages = pretty_tags(osm_data)
                        bot.sendMessage(usr_id, messages, disable_web_page_preview='true')
                elif message.startswith("/about"):
                    response = ["OpenStreetMap bot info:\n\nCREDITS&CODE\n\xF0\x9F\x91\xA5 Author: OSM català (Catalan OpenStreetMap community)\n\xF0\x9F\x94\xA7 Code: https://github.com/Xevib/osmbot\n\xE2\x99\xBB License: GPLv3, http://www.gnu.org/licenses/gpl-3.0.en.html\n\nNEWS\n\xF0\x9F\x90\xA4 Twitter: https://twitter.com/osmbot_telegram\n\nRATING\n\xE2\xAD\x90 Rating&reviews: http://storebot.me/bot/osmbot\n\xF0\x9F\x91\x8D Please rate me at: https://telegram.me/storebot?start=osmbot\n\nThanks for use @OSMbot!!"]
                elif re.match("/search.*",message) is not None and message[8:] != "":
                    search = message[8:].replace("\n","").replace("\r", "")
                    t = 'Results for "{0}":\n\n'.format(search)
                    results = nom.query(search)
                    if len(results) ==0:
                        response = ['Sorry but I couldn\'t find any result for "{0}" \xF0\x9F\x98\xA2\nBut you can try to improve OpenStreetMap\xF0\x9F\x94\x8D\nhttp://www.openstreetmap.org'.format(search)]
                    if len(results) == 1:
                        for result in results:
                            t += "\xF0\x9F\x93\xAE "+result["display_name"]+"\n"
                            print "id:"+str(result['osm_id'])+" type:"+str(result['osm_type'])
                            try:
                                if result['osm_type'] == 'node':
                                    osm_data = api.NodeGet(int(result['osm_id']))
                                elif result['osm_type'] == 'way':
                                    osm_data = api.WayGet(int(result['osm_id']))
                                else:
                                    osm_data = api.RelationWayGet(int(result['osm_id']))
                            except:
                                osm_data = None
                            if osm_data is not None and 'phone' in osm_data['tag']:
                                response.append(t)
                                t = ""
                                response.append("\xF0\x9F\x93\x9E "+osm_data['tag']['phone']+"\n")
                        t += "\xF0\x9F\x93\x8D http://www.openstreetmap.org/?minlat={0}&maxlat={1}&minlon={2}&maxlon={3}&mlat={4}&mlon={5}\n".format(result['boundingbox'][0],result['boundingbox'][1],result['boundingbox'][2],result['boundingbox'][3],result['lat'],result['lon'])
                    else:
                        for result in results:
                            print "id:"+str(result['osm_id'])+" type:"+str(result['osm_type'])
                            t += "\xE2\x96\xB6 "+result["display_name"]+"\n\n"
                            t += "\xF0\x9F\x93\x8D http://www.openstreetmap.org/?minlat={0}&maxlat={1}&minlon={2}&maxlon={3}&mlat={4}&mlon={5}\n\n".format(result['boundingbox'][0],result['boundingbox'][1],result['boundingbox'][2],result['boundingbox'][3],result['lat'],result['lon'])
                            t += "More info /details{0}".format(result['osm_id'])+"\n\n"

                        t += "\xC2\xA9 OpenStreetMap contributors\n"
                elif re.match("/search.*",message) is not None:
                    response = ["Please indicate what are you searching with command /search <search term>"]
                else:
                    response = ["Use /search <search term> command to indicate what you are searching"]
                response.append(t)
                t = ""
                bot.sendMessage(usr_id, response,disable_web_page_preview='true')
            last_id = query["update_id"]
            f = open("last.id", "w")
            f.write(str(last_id))
            f.close()
    sc.enter(15, 1, attend, (sc,))

f = open("token", "r")
token = f.read()
f.close()

token = token.replace("\n", "").replace("\r", "")
api = OsmApi()
nom = nominatim.Nominatim()
bot = OSMbot(token)

s = sched.scheduler(time.time, time.sleep)
s.enter(1, 1, attend, (s,))
s.run()


