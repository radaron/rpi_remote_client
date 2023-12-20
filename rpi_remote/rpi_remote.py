import time
import os
import configparser
import logging.handlers
import requests
from requests.exceptions import ConnectionError # pylint: disable=redefined-builtin
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
        self._logger = self._init_logger()
        self._config = self._load_config()

    def _init_logger(self):
        syslog = logging.handlers.SysLogHandler(address="/dev/log")
        syslog.setFormatter(logging.Formatter('rpi-remote %(name)s: %(levelname)s %(message)s'))
        logger = logging.getLogger("rpi-remote")
        logger.addHandler(syslog)
        logger.setLevel(logging.INFO)
        return logger

    def _load_config(self):
        config = configparser.ConfigParser()
        if config.read(self.CONFIG_PATH):
            return config
        return self._create_config()

    def _create_config(self):
        if not os.path.exists(self.CONFIG_FOLDER_PATH):
            os.makedirs(self.CONFIG_FOLDER_PATH)
        config = configparser.ConfigParser()
        for section, configs in self.DEFAULT_CONFIG.items():
            config[section] = {}
            for config_key, config_value in configs.items():
                config[section][config_key] = config_value
        with open(self.CONFIG_PATH, 'w', encoding='utf-8') as f:
            config.write(f)
        return config

    def _get_order(self):
        url = f"{self._config['connection']['host_address']}/rpi/api/order"
        client_name = self._config['connection']['client_name']
        request = requests.get(url, headers={'name': client_name}, timeout=5)
        return request.json()

    def run(self):
        self._logger.info("Starting rpi-remote client...")
        while True:
            try:
                if data := self._get_order():
                    forwarder = ClientForwarder(**data, logger=self._logger)
                    forwarder.start()
            except ConnectionError as e:
                self._logger.warning("Cannot connect to host: '%s'", e.request.url)
            except Exception as e: # pylint: disable=broad-except
                self._logger.error(e)
            finally:
                time.sleep(int(self._config['connection']['period_time_sec']))

def main():
    client = RpiRemoteClient()
    client.run()
