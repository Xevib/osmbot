# -*- coding: UTF-8 -*-

from __future__ import absolute_import
import unittest
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from bot.osmbot import OsmBot
from bot.error import OSMError
from bot.utils import getData

class OsmBotMock(OsmBot):
    def __init__(self, *args, **kwargs):
        super(OsmBotMock, self).__init__(*args, **kwargs)


class BotTest(unittest.TestCase):
    # instantiate OsmBotMock class
    b = OsmBotMock({}, auto_init=False)

    def test_config_file(self):
        """
        Test for configuraciont file

        :return:None
        """
        from configobj import ConfigObj
        config = ConfigObj('test/bot.conf')
        
        self.assertEqual(config['database'  ], 'bot')
        self.assertEqual(config['user'      ], 'postgres')
        self.assertEqual(config['host'      ], '127.0.0.1')
        self.assertEqual(config['password'  ], 'password')
        self.assertEqual(config['hooks'     ], 'true')
        self.assertEqual(config['webhook'   ], 'https://example.com:443/hook/')
        self.assertEqual(config['sentry_dsn'], 'sync+http://aadfsaa5@example.com:9000/1')
        self.assertEqual(config['token'     ], '32111224414:AAF0BqwSgFKTzkgTkJLcLBKVb2ebrSXbWX4')
        self.assertEqual(config['update_interval'], '10')

    def test_init_config_error(self):
        """
        Test for empty config file

        :return: None
        """

        from configobj import ConfigObj
        config = ConfigObj()
 
        # no config and empty config
        self.assertRaises(OSMError, self.b.init_config, 0)
        self.assertRaises(OSMError, self.b.init_config, True)
        self.assertRaises(OSMError, self.b.init_config, 'random_string')
        self.assertRaises(OSMError, self.b.init_config, config)

    def test_init_config(self):
        from configobj import ConfigObj
        config = ConfigObj('test/bot.conf')

        # TODO(edgar/xevi): let's see if we can test the
        # real api with a fake config

        # self.b.init_config(config)

    def test_languages(self):
        """
        Test to ensure that languages on the locales dir are on the code

        :return: None
        """
        lang_dirs = os.listdir('bot/locales')
        msg = '{} not found in directory in avaible languages but found in bo/locales'
        for lang_dir in lang_dirs:
            is_dir = os.path.isdir(os.path.join('bot/locales', lang_dir))
            if is_dir and lang_dir not in self.b.get_languages().values():
                print(msg.format(lang_dir))
                self.assertTrue(lang_dir in self.b.get_languages().values())

    def test_templates(self):
        """
        Just to check templates syntax

        :return: None
        """

        from jinja2 import Environment, exceptions
        jinja_env = Environment(extensions=['jinja2.ext.i18n'])
        templates = os.listdir('bot/templates')
        for template in templates:
            print('Testing template:{}'.format(template))
            with open(os.path.join('bot/templates', template)) as f:
                template_text = unicode(f.read())
            try:
                jinja_env.from_string(template_text).render()
            except exceptions.TemplateAssertionError:
                pass
            except exceptions.UndefinedError:
                pass

    def test_getData(self):
        self.assertEqual(getData(343535, 'rel'),getData(343535))
        self.assertEqual(getData(423454728, 'way'),getData(423454728))
        self.assertEqual(getData(2482096156, 'nod'), getData(2482096156))
        getData(-1)


if __name__ == '__main__':
    unittest.main()
