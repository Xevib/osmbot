from __future__ import absolute_import
import unittest
import os


class BotTest(unittest.TestCase):
    def test_languages(self):
        from bot.osmbot_blueprint import avaible_languages
        lang_dirs = os.listdir('bot/locales')
        for lang_dir in lang_dirs:
            if os.path.isdir(lang_dir) and lang_dir not in avaible_languages.values():
                print '{} not found in directory in avaible languages but found in bo/locales'.format(lang_dir)
                self.assertTrue(lang_dir in avaible_languages.values())

if __name__ == '__main__':
    unittest.main()
