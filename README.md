# Cradlewise Smart Crib for Home Assistant

Home Assistant integration for the [Cradlewise Smart Crib](https://www.cradlewise.com/) using the unofficial API.

> **Note:** This uses an unofficial API. Cradlewise may change or restrict access at any time.

## Features

| Entity | Type | Description |
|--------|------|-------------|
| Sleep phase | Sensor | Current sleep state (away/awake/stirring/sleep) |
| Baby present | Binary sensor | Baby detected in crib |
| Bouncing | Binary sensor | Rocking motor active |
| Music playing | Binary sensor | White noise / music active |
| Light on | Binary sensor | Nightlight active |
| Soothe count | Sensor | Soothing interventions today |
| Total sleep | Sensor | Total sleep time today |
| Temperature | Sensor | Crib room temperature |
| Music track | Sensor | Current sound machine track name |
| Sleep time | Sensor | Timestamp when baby fell asleep |
| Wake time | Sensor | Timestamp of last wake-up |
| Bounce limit | Sensor | Max allowed rocking intensity |
| Volume limit | Sensor | Max allowed volume level |

Real-time updates via MQTT when available, with REST polling fallback.

## Installation

[![Add to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jlamendo&repository=ha-cradlewise&category=integration)

Or manually: copy `custom_components/cradlewise` to your HA `config/custom_components/` directory.

## Setup

1. Restart Home Assistant
2. Go to **Settings → Devices & Services → Add Integration**
3. Search for **Cradlewise**
4. Enter your Cradlewise account email and password
