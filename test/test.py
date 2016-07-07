import unittest
import os


class BotTest(unittest.TestCase):
    def test_languages(self):
        from bot.osmbot_blueprint import avaible_languages
        lang_dirs = os.listdir('../bot/locales')
        for lang_dir in lang_dirs:
            self.assertTrue(lang_dir in avaible_languages.values())

if __name__ == '__main__':
    unittest.main()
