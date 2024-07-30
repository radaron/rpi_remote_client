![PyPI - Version](https://img.shields.io/pypi/v/rpi-remote?style=for-the-badge&logo=python&logoColor=yellow&link=https%3A%2F%2Fpypi.org%2Fproject%2Frpi-remote%2F)

# Rpi Remote client

## Installation

### Install/Upgrade package
``` shell
python3 -m pip install --upgrade rpi-remote --user
```

### Create service
``` shell
echo "[Unit]
Description=rpi_remote service
After=multi-user.target
Conflicts=getty@tty1.service
[Service]
User=${USER}
Type=simple
Environment="LC_ALL=C.UTF-8"
Environment="LANG=C.UTF-8"
ExecStart=${HOME}/.local/bin/rpi-remote
Restart=on-failure
RestartSec=3
[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/rpi-remote.service
```
``` shell
sudo systemctl daemon-reload
sudo systemctl enable rpi-remote.service
sudo systemctl start rpi-remote.service
```

## Configuartion
Config file path: ```~/.config/rpi_remote/config.ini```

This file automatically generated when the service starts. See the example below.
``` ini
[connection]
server_host = localhost
server_port = 80 # 443 in case of https
ssl = true # true/false
ssh_username = root
ssh_port = 22
period_time_sec = 30
client_name = test_client
disk_path = /media/HDD
```

## Check logs
``` shell
journalctl -fu rpi-remote
```
