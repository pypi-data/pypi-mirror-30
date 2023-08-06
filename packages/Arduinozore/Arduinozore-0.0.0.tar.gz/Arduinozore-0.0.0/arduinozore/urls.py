"""Urls module."""
from handlers.card import CardHandler
from handlers.device import DevicePageHandler
from handlers.index import IndexPageHandler
from handlers.sensor import SensorHandler
from handlers.setting import SettingPageHandler
from handlers.ws import WSHandler
from settings import STATIC_PATH
from tornado.web import StaticFileHandler

url_pattern = [
    (r'/static/(.*)', StaticFileHandler, {'path': STATIC_PATH}),
    (r'/', IndexPageHandler),
    (r'/settings/?$', SettingPageHandler),
    (r'/device/?$', DevicePageHandler),
    (r'/device/((?!create|/)[^/]+)/?$', DevicePageHandler),
    (r'/device/([^/]+)/(?:(edit|create)\w?)?/?', DevicePageHandler),
    (r'/sensor/?$', SensorHandler),
    (r'/sensor/([^/]+)/?$', SensorHandler),
    (r'/sensor/([^/]+)/(?:(edit)\w?)?/?$', SensorHandler),
    (r'/card/?$', CardHandler),
    (r'/card/([^/]+)/?$', CardHandler),
    (r'/card/([^/]+)/(?:(edit)\w?)?/?$', CardHandler),
    (r'/ws/([^/]+)', WSHandler),  # always the last one!
]
