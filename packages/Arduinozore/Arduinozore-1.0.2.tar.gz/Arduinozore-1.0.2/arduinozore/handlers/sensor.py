"""Sensor handler package."""

from models.sensor import Sensor
from tornado.escape import url_escape

from .crudHandler import CrudHandler


class SensorHandler(CrudHandler):
    """Sensor handler."""

    def list(self):
        """List configurations."""
        sensors = Sensor.get_all()
        self.render('sensor/list.html', sensors=sensors)

    def show(self, slug):
        """Show device."""
        sensor = Sensor.get(slug)
        if sensor is not None:
            self.render('sensor/show.html', sensor=sensor, slug=slug)
        else:
            self.redirect('/sensor', permanent=False)

    def create(self):
        """Show configuration form for device."""
        settings = dict()
        settings['sensor'] = None
        settings['method'] = 'post'
        self.render('sensor/config.html', **settings)

    def edit(self, slug):
        """Show configuration form for device."""
        sensor = Sensor.get(slug)
        settings = dict()
        settings['sensor'] = sensor
        settings['method'] = 'put'
        self.render('sensor/config.html', **settings)

    def store(self, slug=""):
        """Create configuration."""
        sensor_name = self.get_argument('name')
        self.save(sensor_name)

    def update(self, slug):
        """Update configuration."""
        self.save(slug)

    def save(self, slug):
        """Save configuration."""
        sensor_name = slug
        min_value = self.get_argument('min_value')
        max_value = self.get_argument('max_value')
        suffix = self.get_argument('suffix')
        reverse = True if 'reverse' in self.request.arguments else False
        sensor = Sensor(sensor_name, min_value, max_value, reverse, suffix)
        sensor.save()
        slug = url_escape(slug)
        redirect_url = self.redirect_url
        if slug not in redirect_url:
            redirect_url += '/' + slug
        self.redirect(redirect_url, permanent=True)

    def destroy(self, slug):
        """Destroy configuration."""
        sensor = Sensor.get(slug)
        sensor.delete()
        self.redirect(self.redirect_url, permanent=False)
