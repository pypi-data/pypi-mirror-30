"""Index page handler package."""
import os
import socket

from models.card import Card
from models.device import Device
from models.sensor import Sensor
from settings import DEVICE_CONFIG_FOLDER
from settings import SSL_PORT
from settings import path

from .crudHandler import CrudHandler
from .tools import get_arduino
from .tools import get_config_name


class DevicePageHandler(CrudHandler):
    """Device page handler."""

    default_args = {'enabled': '', 'name': '', 'type': ''}

    def list(self):
        """List configuration."""
        devices = Device.get_all()
        self.render('device/list.html', devices=devices)

    def show(self, slug):
        """Show device."""
        device = Device.get(Device.get_identifier_from_serial(slug))
        if device is None:
            device = Device.get_config(slug)
            if device is None:
                self.redirect(self.redirect_url + '/create', permanent=False)
            else:
                settings = dict()
                settings['device'] = device
                settings['slug'] = slug
                self.render('device/show.html', **settings)
        else:
            the_host = socket.gethostname()
            settings = dict()
            settings['host'] = the_host
            settings['port'] = SSL_PORT
            settings['slug'] = slug
            settings['device'] = device
            self.render('device/communicate.html', **settings)

    def create(self, slug):
        """Show configuration form for device."""
        cards = Card.get_all()
        sensors = Sensor.get_all()
        device = Device.get(slug)
        if 'card' in self.request.arguments:
            card = Card.get(self.get_argument('card'))
        else:
            card = None
        settings = dict()
        settings['method'] = 'post'
        settings['cards'] = cards
        settings['card'] = card
        settings['sensors'] = sensors
        settings['device'] = device
        settings['slug'] = slug
        settings['method'] = 'post'
        self.render('device/config.html', **settings)

    def edit(self, slug):
        """Show configuration form for device."""
        device = Device.get(Device.get_identifier_from_serial(slug))
        cards = Card.get_all()
        sensors = Sensor.get_all()
        if device is None:
            device = Device.get_config(slug)
            if device is None:
                self.redirect(self.redirect_url + '/create', permanent=False)

        settings = dict()
        settings['method'] = 'put'
        settings['cards'] = cards
        settings['card'] = device.card
        settings['sensors'] = sensors
        settings['device'] = device
        settings['method'] = 'put'
        self.render('device/config.html', **settings)

    def store(self, slug):
        """Store configuration."""
        self.save(slug)

        self.redirect(self.redirect_url, permanent=True)

    def update(self, slug):
        """Update configuration."""
        self.save(slug)

        self.redirect(self.redirect_url, permanent=True)

    def save(self, slug):
        """Save configuration."""
        try:
            self.request.arguments.pop("_method")
        except Exception:
            pass
        device = Device.from_request_args(slug, self.request.arguments)
        device.save()

    def destroy(self, slug):
        """Destroy configuration."""
        arduino = get_arduino(slug)
        config_name = get_config_name(arduino)
        config_file = path(DEVICE_CONFIG_FOLDER, config_name)
        os.remove(config_file)
        self.redirect(self.redirect_url, permanent=False)
