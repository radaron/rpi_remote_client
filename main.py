import time
import os
import requests
from requests.exceptions import ConnectionError
import configparser
import logging.handlers
from forward_client import ClientForwarder

class RpiClient:

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
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.read(config_path)
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
            except ConnectionError as e:
                self.logger.warning("Cannot connect to host: '%s'", e.request.url)
            except Exception as e:
                self.logger.error(e)
            finally:
                time.sleep(int(self.config['connection']['period_time_sec']))

if __name__ == "__main__":
    client = RpiClient()
    client.run()