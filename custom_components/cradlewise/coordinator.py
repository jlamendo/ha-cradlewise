"""DataUpdateCoordinator for Cradlewise."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from pycradlewise import (
    AppConfig,
    CradlewiseApiError,
    CradlewiseClient,
    CradlewiseCradle,
    CradlewiseMqtt,
    SleepAnalytics,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, MQTT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class CradlewiseCoordinator(DataUpdateCoordinator[dict[str, CradlewiseCradle]]):
    """Coordinator to manage fetching Cradlewise data."""

    def __init__(
        self, hass: HomeAssistant, client: CradlewiseClient, app_config: AppConfig
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client
        self._app_config = app_config
        self.cradles: dict[str, CradlewiseCradle] = {}
        self.analytics: dict[str, SleepAnalytics] = {}
        self._mqtt = CradlewiseMqtt()
        self._mqtt_started = False

    @property
    def mqtt_connected(self) -> bool:
        return self._mqtt.available

    async def _async_setup(self) -> None:
        try:
            self.cradles = await self.client.discover_cradles()
        except CradlewiseApiError as err:
            raise UpdateFailed(f"Failed to discover cradles: {err}") from err

    async def _start_mqtt(self) -> None:
        if self._mqtt_started:
            return

        creds = self.client.auth.credentials
        if not creds or not self.cradles:
            return

        try:
            await self._mqtt.connect(
                access_key=creds.access_key,
                secret_key=creds.secret_key,
                session_token=creds.session_token,
                cradle_ids=list(self.cradles.keys()),
                on_state_update=self._on_mqtt_state_update,
                iot_endpoint=self._app_config.iot_endpoint,
            )
            self._mqtt_started = True

            if self._mqtt.available:
                self.update_interval = timedelta(seconds=MQTT_SCAN_INTERVAL)
                _LOGGER.info(
                    "MQTT active — REST poll interval set to %ds", MQTT_SCAN_INTERVAL
                )
        except Exception:
            _LOGGER.debug("MQTT setup failed, continuing with REST polling")

    def _on_mqtt_state_update(self, cradle_id: str, state: dict[str, Any]) -> None:
        cradle = self.cradles.get(cradle_id)
        if not cradle:
            return
        cradle.update_state(state)
        cradle.online = True
        self.async_set_updated_data(self.cradles)

    async def _async_update_data(self) -> dict[str, CradlewiseCradle]:
        if not self.cradles:
            await self._async_setup()

        if not self._mqtt_started:
            await self._start_mqtt()

        if self._mqtt_started and not self._mqtt.available:
            creds = self.client.auth.credentials
            if creds:
                await self._mqtt.reconnect(
                    access_key=creds.access_key,
                    secret_key=creds.secret_key,
                    session_token=creds.session_token,
                    cradle_ids=list(self.cradles.keys()),
                    on_state_update=self._on_mqtt_state_update,
                    iot_endpoint=self._app_config.iot_endpoint,
                )

        for cradle in self.cradles.values():
            try:
                await self.client.update_cradle(cradle)
            except CradlewiseApiError as err:
                _LOGGER.warning("Failed to update %s: %s", cradle.cradle_id, err)

        for cradle in self.cradles.values():
            if cradle.baby_id:
                try:
                    self.analytics[cradle.baby_id] = (
                        await self.client.fetch_sleep_analytics(cradle)
                    )
                except Exception as err:
                    _LOGGER.debug("Analytics fetch failed for %s: %s", cradle.baby_id, err)

        return self.cradles

    async def async_shutdown(self) -> None:
        await self._mqtt.disconnect()
        await super().async_shutdown()
