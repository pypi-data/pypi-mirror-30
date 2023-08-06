"""Index page handler package."""

from .baseHandler import BaseHandler


class SettingPageHandler(BaseHandler):
    """Index page handler."""

    def get(self):
        """Handle get request."""
        available_settings = {'Cartes': 'card',
                              'Capteurs': 'sensor', 'Devices': 'device'}
        self.render('settings.html', available_settings=available_settings)
