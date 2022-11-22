# Install instructions

## Run install script
```
curl -sSL https://gist.githubusercontent.com/radaron/4f844cca0ba09c8521cf13c29fbddfe1/raw | bash
```

## Edit config
Config file path: *~/.config/rpi_remote/config.ini*

## Start service
```
sudo systemctl start rpi-remote
```

# Check logs
```
journalctl -f | grep rpi-remote
```