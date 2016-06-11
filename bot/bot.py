# -*- coding: utf-8 -*-
import json
import requests


class InputTextMessageContent(object):
    def __init__(self, message_text, parse_mode,
                 disable_web_page_preview=False):
        self.message_text = message_text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview


class InlineQueryResultArticle(object):
    def __init__(self, type, id, title, input_message_content,
                 reply_markup=None, url=None, hide_url=None, description=None,
                 thumb_url=None, thumb_width=None, thumb_height=None):
        self.type = 'article'
        self.id = id
        self.title = title
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup
        self.url = url
        self.hide_ur = hide_url
        self.description = description
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height


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
    def __init__(self, keyboard, resize_keyboard=None, one_time_keyboard=None,
                 selective=None):
        if not isinstance(keyboard, list):
            keyboard = [keyboard]
        self.keyboard = [KeyboardButton(k) for k in keyboard]
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.selective = selective

    def addButton(self, text):
        self.keyboard.append(KeyboardButton(text))

    def get_keyboard(self):
        data = {}
        keyboard = []
        for button in self.keyboard:
            keyboard.append([button.text])
        if keyboard:
            data['keyboard'] = keyboard
        if self.resize_keyboard is not None:
            if self.resize_keyboard:
                data['resize_keyboard'] = True
            else:
                data['resize_keyboard'] = False

        if self.one_time_keyboard is not None:
            if self.one_time_keyboard:
                data['one_time_keyboard'] = True
            else:
                data['one_time_keyboard'] = False

        if self.selective is not None:
            if self.selective:
                data['selective'] = True
            else:
                data['selective'] = False
        return data


class ReplyKeyboardHide(object):
    def __init__(self, hide_keyboard=True, selective=None):
        self.hide_keyboard = hide_keyboard
        self.selective = selective

    def get_keyboard(self):
        data = {}
        if self.hide_keyboard:
            data['hide_keyboard'] = True
        else:
            data['hide_keyboard'] = False
        if self.selective is not None:
            if self.selective:
                data['selective'] = True
            else:
                data['selective'] = False
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
                'reply_markup': json.dumps(self.reply_markup.get_keyboard()),
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
        return ret


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

        response = requests.get(
            self.url.format(self.token, method), params=params,
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
        if not isinstance(messages, list):
            messages = [messages]
        method = 'sendMessage'
        resp = False
        for message in messages:
            print 'enviat'
            print json.dumps(message.get_message(), sort_keys=True,
                             indent=4, separators=(',', ': '))
            resp = requests.get(
                self.url.format(self.token, method),
                params=message.get_message())
            if resp.status_code != 200:
                raise Exception(json.loads(resp.content)['description'])

        return resp

    def answerInlineQuery(self, inline_query_id, results, cache_time=None,
                          is_personal=None, next_offset=None, switch_pm_text=None,
                          switch_pm_parameter=None):
        method = 'answerInlineQuery'
        answer = {
            'inline_query_id': inline_query_id,
            'results': [r for r in results]
        }
        if cache_time:
            answer['cache_time'] = cache_time
        if is_personal:
            answer['is_personal'] = is_personal
        if next_offset:
            answer['next_offset'] = next_offset
        if switch_pm_text:
            answer['switch_pm_text'] = switch_pm_text
        if switch_pm_parameter:
            answer['switch_pm_parameter'] = switch_pm_parameter

        resp = requests.get(self.url.format(self.token, method), params=answer)
        print resp
        if resp.status_code != 200:
            raise Exception(json.loads(resp.content)['description'])
