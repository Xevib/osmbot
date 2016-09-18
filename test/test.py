# -*- coding: UTF-8 -*-

from __future__ import absolute_import, unicode_literals
import unittest
import os
from six.moves import reload_module
import sys
reload_module(sys)
sys.setdefaultencoding('utf-8')

from bot.osmbot import OsmBot
from bot.error import OSMError
from bot.utils import getData
from bot.user import User
from configobj import ConfigObj


class OsmBotMock(OsmBot):
    def __init__(self, *args, **kwargs):
        super(OsmBotMock, self).__init__(*args, **kwargs)


class BotTest(unittest.TestCase):
    """
    Unittest for the bot
    """
    def setUp(self):
        """
        Unittest setup
        :return: Noe
        """
        # instantiate OsmBotMock class
        config = {
            'host': 'localhost',
            'database': 'bot',
            'user': 'postgres',
            'token': '32111224414:AAF0BqwSgFKTzkgTkJLcLBKVb2ebrSXbWX4'
        }
        self.osmbot = OsmBotMock(ConfigObj(config), auto_init=True)

    def test_config_file(self):
        """
        Test for configuration file

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
        self.assertRaises(OSMError, self.osmbot.init_config, 0)
        self.assertRaises(OSMError, self.osmbot.init_config, True)
        self.assertRaises(OSMError, self.osmbot.init_config, 'random_string')
        self.assertRaises(OSMError, self.osmbot.init_config, config)

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
            if is_dir and lang_dir not in self.osmbot.get_languages().values():
                print(msg.format(lang_dir))
                self.assertTrue(lang_dir in self.osmbot.get_languages().values())

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
        getData(343535, 'rel')
        getData(423454728, 'way')
        getData(2482096156, 'nod')

    def test_user(self):
        u = User('localhost', 'bot', 'postgres', 'empty')

    def test_render_cache(self):
        """
        Test to check the render_cache method
        :return: None
        """

        self.assertFalse(self.osmbot._check_render_cache(''))
        self.assertEqual(self.osmbot._check_render_cache('1,1,1,1'), 'OK')


if __name__ == '__main__':
    unittest.main()
