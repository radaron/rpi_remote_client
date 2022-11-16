# Install instructions

## Setting configuration
```
cp config.ini.sample config.ini
```
Edit the  relevant fields

## Run install script
```
./install.sh
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