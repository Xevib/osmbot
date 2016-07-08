import unittest
import os


class BotTest(unittest.TestCase):
    def test_languages(self):
        print os.getcwd()
        from bot import avaible_languages
        lang_dirs = os.listdir('bot/locales')
        for lang_dir in lang_dirs:
            if lang_dir not in avaible_languages.values():
                print '{} not found in directory in avaible languages but found in bo/locales'.format(lang_dir)
            self.assertTrue(lang_dir in avaible_languages.values())

if __name__ == '__main__':
    unittest.main()
