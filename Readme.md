# Install instructions

## Run install script
```
curl -sSL https://gist.githubusercontent.com/radaron/4f844cca0ba09c8521cf13c29fbddfe1/raw | bash
```

# Start/Restart/Stop service
```
sudo systemctl start rpi_remote
sudo systemctl restart rpi_remote
sudo systemctl stop rpi_remote
```

# Check logs
```
journalctl -f | grep rpi-remote
```