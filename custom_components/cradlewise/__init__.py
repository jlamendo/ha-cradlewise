"""The Cradlewise Smart Crib integration."""

from __future__ import annotations

import logging
from pathlib import Path

from pycradlewise import CradlewiseAuth, CradlewiseAuthError, CradlewiseClient, get_app_config

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_EMAIL, CONF_PASSWORD, PLATFORMS
from .coordinator import CradlewiseCoordinator

_LOGGER = logging.getLogger(__name__)

type CradlewiseConfigEntry = ConfigEntry[CradlewiseCoordinator]


def _cache_dir(hass: HomeAssistant) -> Path:
    """Return the cache directory for pycradlewise config."""
    return Path(hass.config.config_dir) / ".storage" / "cradlewise"


async def async_setup_entry(hass: HomeAssistant, entry: CradlewiseConfigEntry) -> bool:
    """Set up Cradlewise from a config entry."""
    app_config = await get_app_config(cache_dir=_cache_dir(hass))

    auth = CradlewiseAuth(
        email=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
        app_config=app_config,
    )

    try:
        await auth.authenticate()
    except CradlewiseAuthError as err:
        _LOGGER.error("Failed to authenticate with Cradlewise: %s", err)
        return False

    client = CradlewiseClient(auth)
    coordinator = CradlewiseCoordinator(hass, client, app_config)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: CradlewiseConfigEntry
) -> bool:
    """Unload a Cradlewise config entry."""
    coordinator: CradlewiseCoordinator = entry.runtime_data
    await coordinator.async_shutdown()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
