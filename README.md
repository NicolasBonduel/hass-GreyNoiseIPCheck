# GreyNoise IP Check for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration that periodically checks if your public IP address has been observed scanning the internet, using the free [GreyNoise Labs Check API](https://check.labs.greynoise.io/).

## What it does

This integration creates a **binary sensor** that reports whether your Home Assistant instance's public IP address is "clean" according to GreyNoise:

- **On (Clean):** Your IP has **not** been observed scanning the internet — no malicious activity detected.
- **Off (Not Clean):** Your IP **has** been observed scanning the internet — this may indicate a compromised device on your network.

### Sensor Attributes

| Attribute | Description |
|-----------|-------------|
| `ip_address` | Your detected public IP address |
| `status` | GreyNoise lookup status (`ok`, `not_found`) |
| `noise` | `true` if your IP has been observed scanning the internet |
| `classification` | GreyNoise classification (e.g., `malicious`, `benign`, or `null`) |
| `common_business_services` | `true` if the IP is associated with common business services |
| `trust_level` | GreyNoise trust level for the IP |

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu → **Custom repositories**
3. Add this repository URL and select **Integration** as the category
4. Search for "GreyNoise IP Check" and install it
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/greynoise_ip_check` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for "GreyNoise IP Check"
3. Click **Submit** — no API key is required

The integration uses the free GreyNoise Labs check API, which automatically detects your public IP and checks it. Data is refreshed every 4 hours.

## Automations

Example automation to alert when your IP is flagged:

```yaml
automation:
  - alias: "Alert on GreyNoise IP flagged"
    trigger:
      - platform: state
        entity_id: binary_sensor.greynoise_ip_check_ip_clean
        to: "off"
    action:
      - service: notify.notify
        data:
          title: "⚠️ IP Reputation Alert"
          message: >
            Your public IP {{ state_attr('binary_sensor.greynoise_ip_check_ip_clean', 'ip_address') }}
            has been flagged by GreyNoise as {{ state_attr('binary_sensor.greynoise_ip_check_ip_clean', 'classification') }}.
            This could indicate a compromised device on your network.
```

## How it works

- Uses `https://check.labs.greynoise.io/api/v1/check` — a free, no-auth API
- The API automatically detects the calling IP address
- Polls every 4 hours to stay well within any rate limits
- No API key or account required

## License

MIT
