import time
import os
import requests
from requests.exceptions import ConnectionError
import configparser
import logging.handlers
from .forward import ClientForwarder


class RpiRemoteClient:

    CONFIG_FOLDER_PATH = os.path.join(os.path.expanduser('~'), ".config", "rpi_remote")
    CONFIG_PATH = os.path.join(CONFIG_FOLDER_PATH, "config.ini")
    DEFAULT_CONFIG = {
        "connection": {
            "host_address": "http://localhost:8080",
            "period_time_sec": "30",
            "client_name": "test_client",
        }
    }

    def __init__(self):
        self.logger = self.init_logger()
        self.config = self.load_config()

    def init_logger(self):
        syslog = logging.handlers.SysLogHandler(address="/dev/log")
        syslog.setFormatter(logging.Formatter('rpi-remote %(name)s: %(levelname)s %(message)s'))
        logger = logging.getLogger("rpi-remote")
        logger.addHandler(syslog)
        logger.setLevel(logging.INFO)
        return logger

    def load_config(self):
        config = configparser.ConfigParser()
        if config.read(self.CONFIG_PATH):
            return config
        return self.create_config()

    def create_config(self):
        if not os.path.exists(self.CONFIG_FOLDER_PATH):
            os.makedirs(self.CONFIG_FOLDER_PATH)
        config = configparser.ConfigParser()
        for section in self.DEFAULT_CONFIG:
            config[section] = {}
            for k, v in self.DEFAULT_CONFIG[section].items():
                config[section][k] = v
        with open(self.CONFIG_PATH, 'w') as f:
            config.write(f)
        return config

    def get_order(self):
        url = f"{self.config['connection']['host_address']}/rpi/order"
        client_name = self.config['connection']['client_name']
        request = requests.get(url, headers={'name': client_name}, timeout=5)
        return request.json()

    def run(self):
        self.logger.info("Starting rpi-remote client...")
        while True:
            try:
                if data := self.get_order():
                    data['logger'] = self.logger
                    forwarder = ClientForwarder(**data)
                    forwarder.start()
                time.sleep(int(self.config['connection']['period_time_sec']))
            except ConnectionError as e:
                self.logger.warning("Cannot connect to host: '%s'", e.request.url)
            except Exception as e:
                self.logger.error(e)
            except KeyboardInterrupt:
                return

def main():
    client = RpiRemoteClient()
    client.run()