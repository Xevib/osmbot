# -*- coding: utf-8 -*-
import json
import requests

class OSMbot(object):
    def __init__(self, token):
        self.token=token
        self.url = "https://api.telegram.org/bot{0}/{1}"

    def getUpdates(self, offset=None, limit=None, timeout=None):
        method = "getUpdates"
        params = {
            'offset': offset,
            'limit': limit,
            'timeout': timeout
        }
        return json.loads(requests.get(self.url.format(self.token,method),params=params).content)

    def setWebhook(self):
        method = "setWebhook"
        params = {}
        response = requests.get(self.url.format(self.token,method),params=params)
        return response.content

    def sendMessage(self, chat_id, text, disable_web_page_preview=None, reply_to_message_id=None, reply_markup=None):
        method = "sendMessage"
        params = {
            'chat_id': chat_id,
            'text':text,
            'disable_web_page_preview':disable_web_page_preview,
            'reply_to_message_id':reply_to_message_id,
            'reply_markup':reply_markup
        }

        return json.loads(requests.get(self.url.format(self.token, method), params=params).content)
