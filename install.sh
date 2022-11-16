#!/bin/bash


python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

echo "[Unit]
Description=rpi_remote service
After=multi-user.target
Conflicts=getty@tty1.service
[Service]
User=${USER}
Type=simple
Environment="LC_ALL=C.UTF-8"
Environment="LANG=C.UTF-8"
ExecStart=$(pwd)/.venv/bin/python main.py
WorkingDirectory=$(pwd)
[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/rpi_remote.service

sudo systemctl daemon-reload
sudo systemctl enable rpi_remote.service
sudo systemctl start rpi_remote.service
