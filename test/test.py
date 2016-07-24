# -*- coding: UTF-8 -*-

from __future__ import absolute_import
import unittest
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from bot.osmbot import OsmBot
from bot.error import OSMError

class OsmBotMock(OsmBot):
    def __init__(self, *args, **kwargs):
        super(OsmBotMock, self).__init__(*args, **kwargs)

class BotTest(unittest.TestCase):
    # instantiate OsmBotMock class
    b = OsmBotMock({}, auto_init=False)

    def test_init_config(self):
        from configobj import ConfigObj
        config = ConfigObj()
 
        # no config and empty config
        self.assertRaises(OSMError, self.b.init_config, 0)
        self.assertRaises(OSMError, self.b.init_config, True)
        self.assertRaises(OSMError, self.b.init_config, 'random.cfg')
        self.assertRaises(OSMError, self.b.init_config, config)

    def test_languages(self):
        lang_dirs = os.listdir('bot/locales')
        for lang_dir in lang_dirs:
            if os.path.isdir(os.path.join('bot/locales', lang_dir)) and \
                    lang_dir not in self.b.get_languages().values():
                print '{} not found in directory in avaible languages ' \
                       'but found in bo/locales'.format(lang_dir)
                self.assertTrue(lang_dir in self.b.get_languages().values())

    def test_templates(self):
        from jinja2 import Environment, exceptions
        jinja_env = Environment(extensions=['jinja2.ext.i18n'])
        templates = os.listdir('bot/templates')
        for template in templates:
            print 'Testing template:{}'.format(template)
            with open(os.path.join('bot/templates', template)) as f:
                template_text = unicode(f.read())
            try:
                jinja_env.from_string(template_text).render()
            except exceptions.TemplateAssertionError:
                pass
            except exceptions.UndefinedError:
                pass


if __name__ == '__main__':
    unittest.main()
