import time
import os
import json
import configparser
import statistics
import logging.handlers
import requests
import psutil
from requests.exceptions import ConnectionError  # pylint: disable=redefined-builtin
from .forward import ClientForwarder


class RpiRemoteClient:  # pylint: disable=too-few-public-methods

    CONFIG_FOLDER_PATH = os.path.join(os.path.expanduser('~'), ".config", "rpi_remote")
    CONFIG_PATH = os.path.join(CONFIG_FOLDER_PATH, "config.ini")
    DEFAULT_CONFIG = {
        "connection": {
            "server_host": "localhost",
            "server_port": "443",
            "ssl": "true",
            "ssh_username": "root",
            "ssh_port": "22",
            "period_time_sec": "30",
            "client_name": "test_client",
            "disk_path": "/media/HDD",
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

    @property
    def _schema(self):
        return "https://" if self._config['connection']['ssl'] == 'true' else "http://"

    @property
    def _server_host(self):
        return self._config['connection']['server_host']

    @property
    def _server_port(self):
        return self._config['connection']['server_port']

    def _get_order(self):
        request = requests.get(
            url=f"{self._schema}{self._server_host}:{self._server_port}/rpi/api/order",
            headers={
                'name': self._config['connection']['client_name'],
                'username': self._config['connection']['ssh_username']
            },
            timeout=5
        )
        return request.json()

    def _send_metrics(self):
        metrics = self._collect_metrics()
        url = f"{self._schema}{self._server_host}:{self._server_port}/rpi/api/metric"
        client_name = self._config['connection']['client_name']
        data = {
            'name': client_name,
            'uptime': metrics['uptime_hous'],
            'cpu_usage': metrics['cpu_percent'],
            'memory_usage': metrics['mem_percent'],
            'disk_usage': metrics['disk_usage'],
            'temperature': metrics['temperature'],
        }
        headers = {'Content-type': 'application/json'}
        requests.put(url, data=json.dumps(data), headers=headers, timeout=5)

    def _collect_metrics(self):
        uptime_sec = time.time() - psutil.boot_time()
        disk_path = self._config['connection']['disk_path'] if \
            os.path.exists(self._config['connection']['disk_path']) else '/'
        return {
            'uptime_hous': int(uptime_sec / 3600),
            'mem_percent': int(psutil.virtual_memory().percent),
            'cpu_percent': self._get_cpu_avarage_load(),
            'disk_usage': int(psutil.disk_usage(disk_path).percent),
            'temperature': self._get_cpu_temperature(),
        }

    @staticmethod
    def _get_cpu_temperature():
        try:
            sensor_data = psutil.sensors_temperatures()
            return int([statistics.mean([i.current for i in value])
                        for key, value in sensor_data.items() if key.startswith('cpu')][0])
        except (IndexError, AttributeError):
            return -1

    @staticmethod
    def _get_cpu_avarage_load():
        try:
            return int([x / psutil.cpu_count() * 100
                        for x in psutil.getloadavg()][1])  # 5 min load average
        except IndexError:
            return -1

    def run(self):
        self._logger.info("Starting rpi-remote client...")
        while True:
            try:
                if data := self._get_order():
                    forwarder = ClientForwarder(host=self._server_host, port=data['port'],
                                                local_port=self._config['connection']['ssh_port'])
                    forwarder.start()
                    self._get_order()
                self._send_metrics()
            except ConnectionError as e:
                self._logger.warning("Cannot connect to host: '%s'", e.request.url)
            except Exception:  # pylint: disable=broad-except
                self._logger.exception("Error occurred")
            finally:
                time.sleep(int(self._config['connection']['period_time_sec']))


def main():
    client = RpiRemoteClient()
    client.run()
