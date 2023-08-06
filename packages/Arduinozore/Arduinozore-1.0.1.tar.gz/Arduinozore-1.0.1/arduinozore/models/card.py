"""Card model package."""
from settings import CARD_CONFIG_FOLDER

from .model import Model


class Card(Model):
    """Card class."""

    yaml_tag = u'!Card'

    def __init__(self, name, nb_input_pins, nb_output_pins):
        """Init card."""
        self.name = name
        self.nb_input_pins = int(nb_input_pins)
        self.nb_output_pins = int(nb_output_pins)

    def save(self):
        """Save card."""
        self.save_yaml(CARD_CONFIG_FOLDER)

    def delete(self):
        """Delete card."""
        self._delete(CARD_CONFIG_FOLDER)

    def __repr__(self):
        """Represent card in order to save it."""
        return "%s(name=%r, nb_input_pins=%r, nb_output_pins=%r)" % (
            self.__class__.__name__, self.name, self.nb_input_pins, self.nb_output_pins)

    @classmethod
    def get_all(cls):
        """Get all card configurations."""
        return cls._get_all(CARD_CONFIG_FOLDER)

    @classmethod
    def get(cls, name):
        """Get card by name."""
        return cls._get(name, CARD_CONFIG_FOLDER)
