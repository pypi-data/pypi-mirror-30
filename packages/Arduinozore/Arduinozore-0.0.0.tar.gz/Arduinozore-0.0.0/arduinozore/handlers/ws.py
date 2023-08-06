"""WebSocket handler package."""
import sys

from tornado.websocket import WebSocketHandler


class WSHandler(WebSocketHandler):
    """WebSocket handler."""

    clients = []
    serial_manager = None

    def __init__(self, *args, **kwargs):
        """Init handler."""
        WSHandler.serial_manager = kwargs.pop('serial_manager')
        super(WSHandler, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        """Check origin."""
        return True

    def open(self, slug):
        """Handle connection opening."""
        print('New connection was opened')
        sys.stdout.flush()

        self.port = slug
        self.write_message("Welcome to my websocket!")
        self.write_message(f'serial used: {slug}')
        datas = WSHandler.serial_manager.get_datas_for_port(slug)
        self.write_message(datas)
        WSHandler.clients.append(self)

    def on_message(self, message):
        """Handle incomming messages."""
        print(message)
        sys.stdout.flush()
        WSHandler.serial_manager.toggle_pin(self.port, int(message))

    def on_close(self):
        """Handle connection closing."""
        print('Connection was closed...')
        sys.stdout.flush()
        WSHandler.clients.remove(self)

    @classmethod
    def write_to_clients(cls):
        """Send message to all clients."""
        for client in cls.clients:
            datas = WSHandler.serial_manager.get_datas_for_port(client.port)
            client.write_message(datas)
