"""Arduinozore setup file."""

from subprocess import check_call

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

INSTALL_CMD = "sudo apt-get install openssl"
CERT_CMD = "./install_cert.sh"


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        """Run post install script."""
        check_call(INSTALL_CMD.split())
        check_call(CERT_CMD.split())
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        """Run post install script."""
        check_call(INSTALL_CMD.split())
        check_call(CERT_CMD.split())
        install.run(self)


setup(
    setup_requires=['pbr'],
    pbr=True,
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
)
