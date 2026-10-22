# Comelit ICONA Intercom

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant custom integration for Comelit VIP intercom systems using the ICONA Bridge protocol.

## Supported Devices

- **Comelit 6722W** - Mini ViP hands-free indoor monitor (4.3" LCD, PoE)
- **Comelit 4899 / 4899M** - Quadra external door entry unit with camera
- **Comelit 6742W** - Mini ViP WiFi monitor
- **Comelit 6741W** - Mini ViP WiFi monitor (kit/single-house)
- **Comelit 6701W** - ViP indoor monitor
- Other Comelit VIP system devices with ICONA Bridge support

## Features

- **Door/gate control** - Open doors and gates via lock entities (momentary pulse)
- **Entrance camera** - Live H.264 video stream via local RTSP server + snapshots
- **Doorbell events** - Real-time ring notifications via local VIP listener or FCM cloud fallback
- **Two-way audio** - Answer incoming calls with ONVIF backchannel audio
- **Auto-provisioning** - Automatically creates a dedicated Home Assistant user on the device
- **DHCP discovery** - Automatic detection of Comelit devices on the network (MAC prefix 00:25:29)

## Entities

| Entity | Platform | Description |
|--------|----------|-------------|
| Door lock | `lock` | Open doors (momentary relay pulse, always reports locked) |
| Actuator lock | `lock` | Open gates/barriers |
| Answer doorbell | `button` | Answer active inbound call with two-way audio |
| Entrance camera | `camera` | Live video + snapshots per entrance panel |
| Doorbell event | `event` | Ring and missed call events per entrance |
| Connectivity | `binary_sensor` | ICONA Bridge reachability |
| Ringing | `binary_sensor` | Active ringing state (auto-clears after 30s) |
| Last ring | `sensor` | Timestamp of most recent ring (persisted) |
| Ring count | `sensor` | Running count of rings (persisted) |
| Events source | `sensor` | Active event source: local, cloud, or none |

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu → Custom repositories
3. Add `https://github.com/rellis-erigon/comelit-HA` as an Integration
4. Search for "Comelit ICONA Intercom" and install
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/comelit_intercom` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services → Add Integration
2. Search for "Comelit ICONA Intercom"
3. Enter the IP address of your Comelit indoor monitor (6722W)
4. The integration will auto-provision a dedicated user, or you can provide a token manually

### Options

- **Enable notifications** - Receive doorbell ring events via Comelit's cloud push (FCM)
- **Enable audio** - Include G.711 audio track in the RTSP stream
- **Auto answer** - Automatically answer incoming calls
- **Verbose logging** - Enable detailed protocol debug logging

## Protocol

This integration communicates with Comelit VIP devices using the ICONA Bridge protocol over TCP port 64100. The protocol uses a custom binary/JSON hybrid format with channel-based multiplexing for authentication, configuration, door control, video streaming, and push notifications.

## Development

This repository is public. Before committing, check that nothing from a real
installation (addresses, names, device ids) has crept in:

```bash
python3 scripts/check-no-site-detail.py
```

Examples use the documentation range `192.0.2.x`.

## Credits

Based on [hass-comelit-icona](https://github.com/simllll/hass-comelit-icona) by @simllll and @nicolas-fricke.

## License

This project is provided as-is for personal use with Comelit VIP intercom systems.
