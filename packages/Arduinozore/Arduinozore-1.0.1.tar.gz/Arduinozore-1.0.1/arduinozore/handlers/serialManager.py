"""Logging process."""
import json
import sys
import time
from multiprocessing import Event
from multiprocessing import Manager
from multiprocessing import Process

from .serialReader import SerialReader


class Singleton(type):
    """
    Singleton metaclass.

    From https://stackoverflow.com/q/6760685/9395299.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Instantiate singleton or return."""
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SerialManager(Process, metaclass=Singleton):
    """Process class."""

    def __init__(self):
        """Init process."""
        Process.__init__(self)
        self.exit = Event()
        self.serial_readers = {}
        self.datas = Manager().dict()
        self.out = Manager().dict()

    def toggle_pin(self, port, pin):
        """Toggle pin on card connected to port."""
        if port not in dict(self.out):
            self.out[port] = pin

        print(port)
        print(self.out[port])
        sys.stdout.flush()

    def get_toggelable_pin(self, port):
        """Return toggelable pins for port."""
        try:
            toggle = self.out[port]
            del self.out[port]
            return toggle
        except KeyError:
            return None

    def set_datas(self, port, datas):
        """Set data from child process."""
        self.datas[port] = json.dumps(datas)

    def get_serial_reader(self, port):
        """Get datas for specified serial port."""
        if port not in self.serial_readers:
            self.serial_readers[port] = SerialReader(port, self)
            self.serial_readers[port].start()

    def get_datas_for_port(self, port):
        """Get datas for serial port."""
        self.get_serial_reader(port)
        try:
            return self.datas[port]
        except KeyError:
            self.datas[port] = 'Initializing reader'
            return self.datas[port]

    def run(self):
        """Run process."""
        while not self.exit.is_set():
            try:
                # print("Manager running")
                sys.stdout.flush()
                time.sleep(1)
            except (KeyboardInterrupt, RuntimeError) as e:
                self.shutdown()
            except Exception as e:
                raise e
            finally:
                for s_r in self.serial_readers:
                    self.serial_readers[s_r].join()

    def shutdown(self):
        """Shut down process."""
        self.exit.set()
