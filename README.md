# Plexamp NFC Controller 🎵

A Python command-line controller that reads Plexamp NFC tags through a PN532 reader and starts the linked album, playlist, track, station, or artist on a local or remote Plexamp player.

## Features

- Runs on **Linux, Windows, and macOS**
- Controls **local or remote** Plexamp players exposing the Plex Companion API
- Supports standard **PN532 UART/USB** readers and **PN532Killer** via USB
- **Automatically reconnects** when the reader is unplugged or unavailable
- Detects and plays **tracks, albums, playlists, stations, or artists**
- Includes optional **systemd** installation for Linux

## Requirements

- Python 3.8 or newer
- A PN532 reader connected through a serial port
- A reachable Plexamp player with remote control enabled
- Internet access while installing Python dependencies

CI tests Python 3.8 and 3.14 on x64 Linux, Windows, and Intel macOS. Apple Silicon macOS is tested with Python 3.14 since older Python builds aren't available for current ARM runners.

## Reader Selection

PN532Killer is automatically detected on every platform when its USB metadata is available.

Standard PN532 readers are automatically selected from `/dev/ttyUSB*` or `/dev/ttyACM*` on Linux. On Windows and macOS, set `PN532_PORT` explicitly so the controller does not probe unrelated serial devices.

List available serial ports with:

```text
python -m serial.tools.list_ports -v
```

Typical port values are:

- Windows: `COM3`
- macOS: `/dev/cu.usbserial-110` or `/dev/cu.usbmodem1101`
- Linux: `/dev/ttyUSB0` or `/dev/ttyACM0`

An explicitly configured port always takes precedence over automatic detection. Setting `PN532_PORT` selects the device but does not force the PN532Killer protocol; Killer behavior still requires matching USB metadata.

## Installation

Clone the repository on the device connected to the NFC reader:

```text
git clone https://github.com/spiercey/plexamp-nfc-uart-python.git
cd plexamp-nfc-uart-python
```

### Linux command line

Create a virtual environment and run the controller directly:

```text
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python main.py
```

### Linux with systemd

The installer targets Debian-based Linux systems and installs a systemd unit:

```text
chmod +x install.sh
./install.sh
```

The included service assumes headless Plexamp defaults of a `pi` user and `/home/pi/plexamp-nfc-uart-python`. Update `plexamp-nfc.service` before running the installer if those values differ.

### macOS

Create a virtual environment and install the dependencies:

```text
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m serial.tools.list_ports -v
```

Run a standard PN532 by specifying its port:

```text
PN532_PORT=/dev/cu.usbserial-110 ./.venv/bin/python main.py
```

For an automatically identified PN532Killer, omit `PN532_PORT`.

### Windows PowerShell

Create a virtual environment and install the dependencies:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m serial.tools.list_ports -v
```

Run a standard PN532 by specifying its port:

```powershell
$env:PN532_PORT = "COM3"
.\.venv\Scripts\python.exe main.py
```

For an automatically identified PN532Killer, leave `PN532_PORT` unset:

```powershell
Remove-Item Env:PN532_PORT -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe main.py
```

Windows and macOS support is for command-line execution. Native services, LaunchAgents, scheduled tasks, packaged applications, and installers are not included.

## Configuration

| Variable       | Default             | Description                                                                                 |
| -------------- | ------------------- | ------------------------------------------------------------------------------------------- |
| `PN532_PORT`   | Automatic detection | Exact serial port for the reader. Required for standard PN532 readers on Windows and macOS. |
| `PLEXAMP_HOST` | `localhost`         | Plexamp hostname or IP address without a URL scheme or port.                                |

Plexamp's Companion API port remains `32500`. For an IPv6 address, include URL
brackets, such as `PLEXAMP_HOST=[fd00::10]`.

Example targeting a remote Plexamp player on macOS or Linux:

```text
PLEXAMP_HOST=plexamp.example.com ./.venv/bin/python main.py
```

Example targeting a remote player from Windows PowerShell:

```powershell
$env:PLEXAMP_HOST = "plexamp.example.com"
.\.venv\Scripts\python.exe main.py
```

To configure the Linux systemd service, create an override:

```text
sudo systemctl edit plexamp-nfc.service
```

Add the settings that apply to the installation:

```ini
[Service]
Environment="PN532_PORT=/dev/ttyUSB0"
Environment="PLEXAMP_HOST=plexamp.example.com"
```

Then reload and restart the service:

```text
sudo systemctl daemon-reload
sudo systemctl restart plexamp-nfc.service
```

## How It Works

1. The controller resolves the configured reader or automatically identifies a supported device.
2. It reads the NDEF URI from a detected NFC tag.
3. It converts the `listen.plex.tv` URL to the configured Plexamp endpoint.
4. It sends the playback command and waits for Plexamp to create an active play queue.

Example output:

```text
NFC reader connected on COM3
Tag detected! UID: 04a224bc59
Parsed tag URL: https://listen.plex.tv/playlists/123456
Detected tag type: Playlist
Local Plexamp URL: http://localhost:32500/playlists/123456
Playback triggered! (Playlist)
```

## Linux Service Management

Check the running status:

```shell
systemctl status plexamp-nfc.service
```

Follow live logs:

```shell
sudo journalctl -f -u plexamp-nfc.service
```

Restart the service:

```shell
sudo systemctl restart plexamp-nfc.service
```

Disable it on boot (optional):

```shell
sudo systemctl disable plexamp-nfc.service
```

## Troubleshooting

| Issue                              | Possible fix                                                                                               |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `Waiting for NFC reader...`        | Run `python -m serial.tools.list_ports -v`; set `PN532_PORT` for an unidentified reader.                   |
| Reader cannot be opened            | Confirm the port name, install the USB serial driver if required, and close other programs using the port. |
| PN532Killer is treated as standard | Check that port enumeration reports VID/PID `1A86:55D3` or a `PN532Killer` product description.            |
| `Failed to trigger Plexamp`        | Confirm Plexamp remote control is enabled and TCP port `32500` is reachable at `PLEXAMP_HOST`.             |
| Linux service does not start       | Check `sudo journalctl -u plexamp-nfc.service -xe` and verify the service user and paths.                  |
| No tags are detected               | Confirm the reader is configured for UART at 115200 baud and try another supported tag.                    |

## License & Credits

MIT License
Created by Stephen Piercey
