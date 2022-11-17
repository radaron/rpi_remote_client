# Install instructions

## Run install script
```
curl -sSL https://gist.githubusercontent.com/radaron/4f844cca0ba09c8521cf13c29fbddfe1/raw | bash
```

## Edit config
```
cp config.ini.sample config.ini
```
Edit the relevan fields.

## Start service
```
sudo systemctl start rpi_remote
```

# Check logs
```
journalctl -f | grep rpi-remote
```