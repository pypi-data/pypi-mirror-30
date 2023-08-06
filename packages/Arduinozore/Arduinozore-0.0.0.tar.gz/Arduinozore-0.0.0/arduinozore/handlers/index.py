"""Index page handler package."""

from models.device import Device

from .baseHandler import BaseHandler


class IndexPageHandler(BaseHandler):
    """Index page handler."""

    def get(self):
        """Handle get request."""
        devices = Device.get_connected_devices()
        self.render('index.html', devices=devices)
