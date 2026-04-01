"""Constants for the Cradlewise HA integration."""

DOMAIN = "cradlewise"

CONF_EMAIL = "email"
CONF_PASSWORD = "password"

# Polling intervals
DEFAULT_SCAN_INTERVAL = 30  # seconds (REST-only fallback)
MQTT_SCAN_INTERVAL = 300  # seconds (when MQTT is active)

PLATFORMS: list[str] = ["sensor", "binary_sensor"]
