# -*- coding: utf-8 -*-
import re
import nominatim
import os
import sched, time
from osmapi import OsmApi
from bot import OSMbot


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
            if "text" in query["message"]:
                message = query["message"]["text"]
                usr_id = query["message"]["chat"]["id"]
                if message.startswith("@osmbot"):
                    message = message[8:]
                if message == "/start":
                    response = "Hi,how I can help you?"
                elif message.startswith( "/about"):
                    response = "OpenStreetMap bot info:\n\nCREDITS&CODE\n\xF0\x9F\x91\xA5 Author: OSM català (Catalan OpenStreetMap community)\n\xF0\x9F\x94\xA7 Code: https://github.com/Xevib/osmbot\n\xE2\x99\xBB License: GPLv3, http://www.gnu.org/licenses/gpl-3.0.en.html\n\nNEWS\n\xF0\x9F\x90\xA4 Twitter: https://twitter.com/osmbot_telegram\n\nRATING\n\xE2\xAD\x90 Rating&reviews: http://storebot.me/bot/osmbot\n\xF0\x9F\x91\x8D Please rate me at: https://telegram.me/storebot?start=osmbot\n\nThanks for use @OSMbot!!"
                elif re.match("/search.*",message) is not None and message[8:] != "":
                    search = message[8:].replace("\n","").replace("\r","")
                    response = 'Results for "{0}" :\n'.format(search)
                    results = nom.query(search)
                    if len(results) ==0:
                        response = 'Sorry but I couldn\'t find any result for "{0}" \xF0\x9F\x98\xA2\nBut you can try to improve OpenStreetMap\xF0\x9F\x94\x8D\nhttp://www.openstreetmap.org'.format(search)
                    else:
                        for result in results:
                            response += "\xF0\x9F\x93\xAE "+result["display_name"]+"\n"
                            try:
                                if result['osm_type']=='node':
                                    osm_data = api.NodeGet(int(result['osm_id']))
                                else:
                                    osm_data = api.WayGet(int(result['osm_id']))
                            except:
                                osm_data = None
                            if osm_data is not None and 'phone' in osm_data['tag']:
                                bot.sendMessage(usr_id, response,disable_web_page_preview='true')
                                response = "\xF0\x9F\x93\x9E "+osm_data['tag']['phone']+"\n"
                                bot.sendMessage(usr_id, response,disable_web_page_preview='true')
                                response = ""
                            response += "\xF0\x9F\x93\x8D http://www.openstreetmap.org/?minlat={0}&maxlat={1}&minlon={2}&maxlon={3}&mlat={4}&mlon={5}\n".format(result['boundingbox'][0],result['boundingbox'][1],result['boundingbox'][2],result['boundingbox'][3],result['lat'],result['lon'])
                            bot.sendMessage(usr_id, response,disable_web_page_preview='true')
                            response = ""
                elif re.match("/search.*",message) is not None:
                    response = "Please indicate what are you searching"
                else:
                    response = "Use /search <search term> command to indicate what you are searching"
                bot.sendMessage(usr_id, response,disable_web_page_preview='true')
            last_id = query["update_id"]
            f = open("last.id" , "w")
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


