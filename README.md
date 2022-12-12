# Rpi Remote client

## Installation

### Prerequisites
* rust
* libffi
* gcc
* openssl

### Install package
```
python3 -m pip install --upgrade rpi-remote --user
```

### Create service
```
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
[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/rpi-remote.service
```
```
sudo systemctl daemon-reload
sudo systemctl enable rpi-remote.service
sudo systemctl start rpi-remote.service
```

## Edit config
Config file path: *~/.config/rpi_remote/config.ini*

## Check logs
```
journalctl -fu rpi-remote
```
