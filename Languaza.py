# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
1. Надо перехватить shortcut переключения языка на Windows
2. Передать это на MacOS
3. И переключить язык на MacOS
"""
import os
import socket

from dotenv import load_dotenv
from pynput import keyboard
from loguru import logger
from pynput.keyboard import Controller, Key

load_dotenv()

# SIDE=MacOS

def main():
    side = os.environ['SIDE']
    logger.debug(f"Work on {side}")

    if side == 'Windows':

        def create_socket():
            logger.debug('Create socket')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            client_address = os.environ['CLIENT_ADDRESS']
            client_port = int(os.environ['CLIENT_PORT'])
            logger.debug(f"Connect to '{client_address}:{client_port}'")

            sock.connect((client_address, client_port))

            return sock

        def start_keyboard_hooks():
            def on_activate():
                logger.debug('Global hotkey activated!')
                sock = create_socket()
                sock.send("Data 42".encode())
                sock.close()

            def for_canonical(f):
                return lambda k: f(l.canonical(k))

            hotkey = keyboard.HotKey(
                keyboard.HotKey.parse('<alt>+<shift>'), on_activate)

            with keyboard.Listener(
                    on_press=for_canonical(hotkey.press),
                    on_release=for_canonical(hotkey.release)) as l:
                l.join()

        start_keyboard_hooks()

    elif side == 'MacOS':
        def start_socket_server():
            logger.debug('Create socket')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            server_address = os.environ['SERVER_ADDRESS']
            server_port = int(os.environ['SERVER_PORT'])
            logger.debug(f"Bind socket: {server_address}:{server_port}")
            sock.bind((server_address, server_port))

            sock.listen(1)

            keyboard = Controller()

            while True:
                logger.debug('Wait connection')
                connection, client_address = sock.accept()

                logger.debug(f"'{client_address}' connected")

                try:
                    data = connection.recv(1000)
                    logger.debug(f"Recv {data}")

                    keyboard.press(Key.cmd)
                    keyboard.press(Key.space)
                    keyboard.release(Key.space)
                    keyboard.release(Key.cmd)

                finally:
                    connection.close()

        start_socket_server()


if __name__ == '__main__':
    main()
