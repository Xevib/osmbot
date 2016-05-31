# -*- coding: utf-8 -*-
import json
import requests


class KeyboardButton(object):
    def __init__(self, text, request_contact=None, request_location=None):
        self.text = text
        self.request_contact = request_contact
        self.request_location = request_location

    def get_button(self):
        data = {'text': self.text}
        if self.request_contact is not None:
            if self.request_contact:
                data['request_contact'] = 'true'
            else:
                data['request_contact'] = 'false'

        if self.request_location is not None:
            if self.request_location:
                data['request_location'] = 'true'
            else:
                data['request_location'] = 'false'

        return data


class ReplyKeyboardMarkup(object):
    def __init__(self, keyboard, resize_keyboard=None, one_time_keyboard=None, selective=None):
        self.keyboard = keyboard
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.selective = selective

    def get_keyboard(self):
        data = {}
        keyboard = []
        for button in self.keyboard:
            keyboard.append([button.get_button()])
        if self.resize_keyboard is not None:
            if self.resize_keyboard:
                data['resize_keyboard'] = 'true'
            else:
                data['resize_keyboard'] = 'false'

        if self.one_time_keyboard is not None:
            if self.one_time_keyboard:
                data['one_time_keyboard'] = 'true'
            else:
                data['one_time_keyboard'] = 'false'

        if self.selective is not None:
            if self.selective:
                data['selective'] = 'true'
            else:
                data['selective'] = 'false'
        return data


class ReplyKeyboardHide(object):
    def __init__(self, hide_keyboard=True, selective=None):
        self.hide_keyboard = hide_keyboard
        self.selective = selective

    def get_keyboad(self):
        data = {}
        if self.hide_keyboard:
            data['hide_keyboard'] = 'true'
        else:
            data['hide_keyboard'] = 'false'
        if self.selective is not None:
            if self.selective:
                data['selective'] = 'true'
            else:
                data['selective'] = 'false'
        return data


class Message(object):
    def __init__(self, chat_id, text, parse_mode=None, disable_web_page_preview=False, reply_to_message_id=None, reply_markup=None):
        self.chat_id = chat_id
        self.text = text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview
        self.reply_to_message_id = reply_to_message_id
        if reply_markup is not None:
            self.reply_markup = reply_markup
        else:
            self.reply_markup = ReplyKeyboardHide()

    def get_message(self):
        ret = {}
        if self.reply_markup:
            ret.update({
                'chat_id': self.chat_id,
                'text': self.text,
                'disable_web_page_preview': self.disable_web_page_preview,
                'reply_to_message_id': self.reply_to_message_id,
                'reply_markup': self.reply_markup.get_keyboad(),
                'parse_mode': self.parse_mode
            })
        else:
            ret.update({
                'chat_id': self.chat_id,
                'text': self.text,
                'disable_web_page_preview': self.disable_web_page_preview,
                'reply_to_message_id': self.reply_to_message_id,
                'parse_mode': self.parse_mode
            })
        if self.disable_web_page_preview:
            ret['disable_web_page_preview'] = 'true'
        else:
            ret['disable_web_page_preview'] = 'false'
        if type(self.text) == list:
            for t in self.text:
                ret['text'] = t


class OSMbot(object):
    def __init__(self, token):
        self.token = token
        self.url = 'https://api.telegram.org/bot{0}/{1}'

    def getUpdates(self, offset=None, limit=None, timeout=None):
        method = "getUpdates"
        params = {
            'offset': offset,
            'limit': limit,
            'timeout': timeout
        }
        return json.loads(requests.get(self.url.format(self.token, method), params=params).content)

    def setWebhook(self, url=None, certificate=None):
        method = "setWebhook"
        params = {
            'url': url,
            'certificate': certificate
        }

        response = requests.get(self.url.format(self.token,method), params=params,
                                files={'certificate': ('osmbot.crt', certificate)})
        return response.content

    def sendPhoto(self, chat_id, photo, filename, caption=None, reply_to_message_id=None, reply_markup=None):
        method = "sendPhoto"
        params = {
            'chat_id': chat_id,
        }
        if caption is not None:
            params['caption'] = caption
        response = requests.post(self.url.format(self.token, method), params=params, files={'photo': (filename, photo)})
        return response.content

    def sendDocument(self, chat_id, document, filename, reply_to_message_id=None, reply_markup=None):
        method = "sendDocument"
        params = {
            'chat_id': chat_id,
        }
        response = requests.post(self.url.format(self.token, method), params=params, files={'document': (filename, document)})
        return response.content

    def sendMessage(self, messages):
        method = 'sendMessage'
        resp = False
        for message in messages:
            resp = requests.get(
                self.url.format(self.token, method),
                params=message.get_message())
        return resp

