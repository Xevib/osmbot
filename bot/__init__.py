from __future__ import absolute_import
from bot.osmbot_blueprint import osmbot_blueprint


class Osmbot(object):
    def __init__(self, app=None, url_prefix='/'):
        self.url_prefix = url_prefix
        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        app.register_blueprint(osmbot_blueprint, url_prefix=self.url_prefix)
        app.extensions['osmbot'] = self
