"""Sensor model package."""
from settings import SENSOR_CONFIG_FOLDER

from .model import Model


class Sensor(Model):
    """Sensor class."""

    yaml_tag = u'!Sensor'

    def __init__(self, name, min_value, max_value, reverse=False, suffix=""):
        """Init sensor."""
        self.name = name
        self.min_value = int(min_value)
        self.max_value = int(max_value)
        self.reverse = reverse
        self.suffix = suffix

    def save(self):
        """Save sensor."""
        self.save_yaml(SENSOR_CONFIG_FOLDER)

    def delete(self):
        """Delete sensor."""
        self._delete(SENSOR_CONFIG_FOLDER)

    def __repr__(self):
        """Represent sensor in order to save it."""
        return "%s(name=%r, min_value=%r, max_value=%r, reverse=%r, suffix=%r)" % (
            self.__class__.__name__, self.name, self.min_value, self.max_value,
            self.reverse, self.suffix)

    def transform_datas(self, raw_datas):
        """Transform raw datas."""
        d = float(raw_datas)
        if self.reverse:
            return str(round((d / 1024 * (self.min_value-self.max_value) + self.max_value), 1)) + " " + self.suffix
        else:
            return str(round((d / 1024 * (self.max_value-self.min_value) + self.min_value), 1)) + " " + self.suffix

    @classmethod
    def get_all(cls):
        """Get all sensor configurations."""
        return __class__._get_all(SENSOR_CONFIG_FOLDER)

    @classmethod
    def get(cls, name):
        """Get sensor by name."""
        return __class__._get(name, SENSOR_CONFIG_FOLDER)
