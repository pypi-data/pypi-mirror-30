"""Device model package."""

from serial.tools import list_ports
from settings import DEVICE_CONFIG_FOLDER

from .card import Card
from .model import Model


class Port(Model):
    """Port class."""

    yaml_tag = u'!Port'

    def __init__(self, name, number, enabled, _type="output"):
        """Init port."""
        self.name = name
        self._type = _type
        self.number = number
        self.enabled = enabled if enabled is True or False else (
            True if enabled == 'on' else False)

    def __repr__(self):
        """Represent port in order to save it."""
        return "%s(number=%r, name=%r, _type=%r, enabled=%r)" % (
            self.__class__.__name__, self.number, self.name, self._type, self.enabled)


class Device(Model):
    """Device class."""

    yaml_tag = u'!Device'

    def __init__(self, name, identifier, card_name):
        """Init device."""
        self.name = name
        self.identifier = identifier
        self.card = Card.get(card_name)
        self.init_ports()

    def save(self):
        """Save device."""
        self.save_yaml(DEVICE_CONFIG_FOLDER)

    def delete(self):
        """Delete device."""
        self._delete(DEVICE_CONFIG_FOLDER)

    def __repr__(self):
        """Represent device in order to save it."""
        return "%s(name=%r, identifier=%r, card=%r, ports=%r)" % (
            self.__class__.__name__, self.name, self.identifier, self.card, self.ports)

    def init_ports(self):
        """Init port list."""
        self.ports = {'input': list(), 'output': list()}
        for i in range(self.card.nb_input_pins):
            self.ports['input'].append(Port(
                number=i, name="", enabled="False", _type=""))
        for i in range(self.card.nb_output_pins):
            self.ports['output'].append(Port(
                number=i, name="", enabled="False", _type=""))

    def add_port_from_dict(self, port, dict):
        """Create port and add from dict."""
        port = int(port.replace("port", ""))
        if port >= self.card.nb_input_pins:
            port = port - self.card.nb_input_pins
        p = Port(number=port, **dict)
        _type = p._type if p._type == "output" else "input"
        port_to_replace = next(
            (self.ports[_type].index(port) for port in self.ports[_type] if p.number == port.number), None)
        self.ports[_type][port_to_replace] = p

    def get_filename(self):
        """Get filename to save."""
        return __class__.filenamify(self.identifier) + ".yaml"

    @classmethod
    def get_all(cls):
        """Get all device configurations."""
        return __class__._get_all(DEVICE_CONFIG_FOLDER)

    @classmethod
    def get(cls, name):
        """Get device by name."""
        return __class__._get(name, DEVICE_CONFIG_FOLDER)

    @classmethod
    def get_connected_devices(cls):
        """Get devices connected."""
        serials = list(list_ports.comports())
        arduinos = [s for s in serials if 'Arduino' in s.description]
        devices = {a.device: __class__.get(__class__.get_identifier(
            a)) for a in arduinos}
        return devices

    @classmethod
    def get_config(cls, name):
        """Get config by name."""
        configs = cls.get_all()
        if configs is not None:
            return next(
                (config for config in configs if config.name == name), None)
        else:
            return configs

    @classmethod
    def get_identifier_from_serial(cls, serial):
        """Get device identifier from serial name."""
        serials = list(list_ports.comports())
        arduinos = [s for s in serials if 'Arduino' in s.description]
        arduino = next(
            (arduino for arduino in arduinos if serial in arduino.device), None)
        return __class__.get_identifier(arduino)

    @classmethod
    def get_identifier(cls, arduino):
        """Get identifier from arduino."""
        if arduino is not None:
            return f'{arduino.vid}{arduino.pid}{arduino.serial_number}'
        else:
            return None

    @classmethod
    def from_request_args(cls, slug, args):
        """Init device from request args."""
        args = {arg: args[arg][0].decode() for arg in args}
        res = dict()
        for arg in args:
            if '[' in arg and ']' in arg:
                split_arg = arg.split('[')
                var_name = split_arg[0]
                index = split_arg[1].split(']')[0]
                if var_name not in res:
                    res[var_name] = dict()
                res[var_name][index] = args[arg]
            else:
                res[arg] = args[arg]
        if 'identifier' not in res:
            identifier = cls.get_identifier_from_serial(slug)
        else:
            identifier = res.pop('identifier')
        dev = cls(res.pop('name'), identifier,
                  res.pop('card_name'))
        for port in res:
            dev.add_port_from_dict(port, res[port])
        return dev
