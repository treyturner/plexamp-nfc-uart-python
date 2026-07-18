# Plexamp NFC Controller 🎵

A simple Python service that lets you trigger **Plexamp playback using NFC tags**.

This script listens for NFC tags via a USB reader (like the **PN532**) and automatically plays the linked item (album, playlist, track, etc.) on your **headless Plexamp** instance — perfect for setups like Raspberry Pi jukeboxes or DIY smart music stations.

---

## 🚀 Features

- Works with local or remote Plexamp players exposing the Plex Companion API
- Compatible with **PN532 UART/USB NFC readers**
- Automatically reconnects if the reader is unplugged or unavailable
- Detects and plays **tracks, albums, playlists, stations, or artists**
- Runs as a **systemd service** for seamless startup and background operation

---

## 🧰 Requirements

- A Linux device for the NFC controller and a reachable Plexamp instance
- A **PN532 NFC reader** connected via USB or UART
  (uses `/dev/ttyUSB*`)
- Python 3.8 or newer
- Internet access for package installation
- The service assumes you are using the default `pi` user from raspberry pi install. If you are using a different user update the `plexamp-nfc.service` prior to install.

---

## 📦 Installation

Clone this repo on the device connected to the NFC reader:

```bash
git clone https://github.com/spiercey/plexamp-nfc-uart-python.git
cd plexamp-nfc-uart-python
```


Then run the installer:

```
chmod +x install.sh
./install.sh
```


This will:

Install all Python dependencies in a virtual environment

Set up and enable the plexamp-nfc.service systemd unit

Start the NFC controller automatically

Once complete, the service should already be running.

## How It Works

The script searches for a PN532 device (/dev/ttyUSB*).

When a tag is detected, it reads the NDEF URI data.

The URI is parsed and converted into the configured Plexamp URL
(e.g. https://listen.plex.tv/... → http://localhost:32500/... by default).

The Plexamp endpoint is triggered via HTTP to start playback.

Example log output:

```
NFC reader connected on /dev/ttyUSB0
Tag detected! UID: 04a224bc59
Parsed tag URL: https://listen.plex.tv/playlists/123456
Detected tag type: Playlist
Local Plexamp URL: http://localhost:32500/playlists/123456
Playback triggered! (Playlist)
```

## Targeting a Remote Plexamp Player

By default, the controller sends playback requests to `localhost:32500`. Set `PLEXAMP_HOST` when Plexamp runs on another device:

```bash
PLEXAMP_HOST=plexamp.example.com python main.py
```

Set the value to a hostname or IP address without a URL scheme or port. Plexamp's companion API port remains `32500`. For an IPv6 address, include the required URL brackets, such as `PLEXAMP_HOST=[fd00::10]`.

For the systemd service, edit the service file:

```bash
sudo systemctl edit plexamp-nfc.service
```

Configure the variable as needed:

```ini
[Service]
Environment="PLEXAMP_HOST=plexamp.example.com"
```

Then reload and restart the service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart plexamp-nfc.service
```

The NFC controller must be able to reach TCP port `32500` on the Plexamp host.

## Monitoring & Logs

Check the running status:

`systemctl status plexamp-nfc.service`

Follow live logs:

`sudo journalctl -f -u plexamp-nfc.service`

Restart the service:

`sudo systemctl restart plexamp-nfc.service`

Disable it on boot (optional):

`sudo systemctl disable plexamp-nfc.service`

## Manual Run (for debugging)

```
source venv/bin/activate
python main.py
```


## Troubleshooting

```
| Issue                       | Possible Fix                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------- |
| `Waiting for NFC reader...` | Check your PN532 connection. Run `ls /dev/ttyUSB*` to confirm the device appears.     |
| `Failed to trigger Plexamp` | Make sure Plexamp headless is running and reachable at the configured host on port `32500`. |
| Service won’t start         | Check logs via `sudo journalctl -u plexamp-nfc.service -xe`.                          |
| No tags detected            | Try different baud rate in `main.py` (`baudrate=115200` by default).                  |

```

## License & Credits

MIT License
Created by Stephen Piercey
