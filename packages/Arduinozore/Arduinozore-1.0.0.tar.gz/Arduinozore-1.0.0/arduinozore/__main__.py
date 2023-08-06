"""Arduinozore module."""

import argparse
import os
import socket
import sys
from shutil import copyfile
from shutil import get_terminal_size
from shutil import rmtree

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from handlers.error404handler import My404Handler
from handlers.serialManager import SerialManager
from handlers.ws import WSHandler
from pyfiglet import Figlet
from settings import ARDUINO_CODE_FILE_NAME
from settings import ARDUINO_FILE_PATH
from settings import CONFIG_FOLDER
from settings import PORT
from settings import SSL_PORT
from settings import path
from settings import settings
from settings import ssl_opts
from urls import url_pattern


def main():
    """Catch main function."""
    p = argparse.ArgumentParser(
        description="Arduinozore server", prog="arduinozore")
    p.add_argument('-hp',
                   '--http_port',
                   type=int,
                   help='Server http port. Default 80')
    p.add_argument('-hsp',
                   '--https_port',
                   type=int,
                   help='Server https port. Default 443. Used for sockets too.')
    p.add_argument('-a',
                   '--arduino',
                   type=str,
                   metavar='path',
                   help='Path where arduino source code will be generated.')
    p.add_argument('--newconfig',
                   action="store_true",
                   help='Delete actual config and make a new one. Warning.')
    args = p.parse_args()

    if args.arduino:
        copy_arduino_code(args.arduino)

    if args.newconfig:
        if os.path.exists(CONFIG_FOLDER):
            rmtree(CONFIG_FOLDER)

    http_port = PORT if args.http_port is None else args.http_port
    ssl_port = SSL_PORT if args.https_port is None else args.https_port

    check_config_folder()

    serial_manager = SerialManager()
    try:
        if not serial_manager.is_alive():
            serial_manager.start()
        url_pattern[-1] = (*url_pattern[-1],
                           {'serial_manager': serial_manager})
        index_application = tornado.web.Application(
            url_pattern, default_handler_class=My404Handler, **settings)

        index_application.listen(http_port)
        http_server = tornado.httpserver.HTTPServer(
            index_application,
            ssl_options=ssl_opts
        )
        http_server.listen(ssl_port)
        tornado.ioloop.PeriodicCallback(WSHandler.write_to_clients, 500).start()

        terminal_width = get_terminal_size((80, 20))[0]
        introduction(ssl_port, terminal_width)

        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print(f"{'Exiting...': ^{terminal_width}}")
    except Exception as e:
        print(e)
        sys.exit()
    finally:
        serial_manager.join()


def introduction(ssl_port, terminal_width):
    """Show a message to the user so he knows who we are."""
    app_name = '  Arduinozore'
    TOPBAR = f"/{'#' * (terminal_width - 2)}\\\n"

    print(TOPBAR)
    print(Figlet(font='banner').renderText(app_name))
    print(f"\{'#' * (terminal_width - 2)}/\n")
    print(TOPBAR)
    HOST = socket.gethostname()
    PORT = ssl_port
    print(f"{f' Listening on: https://{HOST}:{PORT} ': ^{terminal_width}}")
    sys.stdout.flush()


def check_config_folder():
    """Check if config folder exists, otherwise creates it."""
    try:
        if not os.path.exists(CONFIG_FOLDER):
            os.makedirs(CONFIG_FOLDER)
    except Exception as e:
        exit(e)


def copy_arduino_code(dest):
    """Copy arduino source code to dest."""
    dst = path(dest, ARDUINO_CODE_FILE_NAME)
    copyfile(ARDUINO_FILE_PATH, dst)
    print("File copied to " + dst)
    exit(0)


if __name__ == "__main__":
    main()
