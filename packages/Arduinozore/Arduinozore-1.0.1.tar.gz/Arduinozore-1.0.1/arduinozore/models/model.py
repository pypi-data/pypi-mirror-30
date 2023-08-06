"""Default model package."""
import base64
import os

from settings import path
from yaml import SafeLoader
from yaml import YAMLObject
from yaml import dump
from yaml import safe_load


class Model(YAMLObject):
    """Model default class."""

    yaml_tag = u'!Model'
    yaml_loader = SafeLoader

    def __init__(self, name):
        """Init model."""
        self.name = name

    def __repr__(self):
        """Represent model in order to save it."""
        return "%s(name=%r)" % (self.__class__.__name__, self.name)

    @classmethod
    def load_yaml(cls, folder, filename):
        """Load yaml from file."""
        try:
            with open(path(folder, filename), 'r') as f:
                model = safe_load(f)
        except (FileExistsError, FileNotFoundError):
            model = None
        return model

    def save_yaml(self, folder):
        """Save model to file."""
        config_file = self.get_filename()
        config_file = path(folder, config_file)
        with open(config_file, 'w') as f:
            d = dump(self, default_flow_style=False,
                     allow_unicode=True, encoding=None)
            f.write(d)

    def get_filename(self):
        """Get filename to save."""
        return __class__.filenamify(self.name) + ".yaml"

    def _delete(self, folder):
        """Delete model file."""
        os.remove(path(folder, self.get_filename()))

    @classmethod
    def filenamify(cls, name):
        """Return filename base64 encoded from filename."""
        return base64.urlsafe_b64encode(name.encode('UTF-8')).decode()

    @classmethod
    def unfilenamify(cls, filename):
        """Return filename base64 decoded from filename."""
        return base64.urlsafe_b64decode(filename.encode()).decode('UTF-8')

    @classmethod
    def _get_all(cls, folder):
        """Get all models configurations."""
        models = list()
        if not os.path.exists(folder):
            os.makedirs(folder)
        config_files = os.listdir(folder)
        if config_files is not None and len(config_files) > 0:
            for config_file in config_files:
                model = cls.load_yaml(folder, config_file)
                models.append(model)
        else:
            models = None
        return models

    @classmethod
    def _get(cls, name, folder):
        """Get model by name."""
        try:
            model = cls.load_yaml(folder, cls.filenamify(name) + ".yaml")
        except Exception:
            model = None
        return model
