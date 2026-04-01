"""Sensor entities for Cradlewise."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pycradlewise import CradlewiseCradle, SleepAnalytics

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CradlewiseCoordinator


@dataclass(frozen=True, kw_only=True)
class CradlewiseSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[CradlewiseCradle], Any]


@dataclass(frozen=True, kw_only=True)
class CradlewiseAnalyticsEntityDescription(SensorEntityDescription):
    value_fn: Callable[[SleepAnalytics], Any]


SENSOR_DESCRIPTIONS: tuple[CradlewiseSensorEntityDescription, ...] = (
    CradlewiseSensorEntityDescription(
        key="sleep_state",
        translation_key="sleep_state",
        icon="mdi:sleep",
        value_fn=lambda c: c.baby_sleep_state,
    ),
    CradlewiseSensorEntityDescription(
        key="sleep_phase",
        translation_key="sleep_phase",
        icon="mdi:moon-waning-crescent",
        value_fn=lambda c: c.sleep_phase_name,
    ),
    CradlewiseSensorEntityDescription(
        key="cradle_mode",
        translation_key="cradle_mode",
        icon="mdi:baby-carriage",
        value_fn=lambda c: c.cradle_mode,
    ),
    CradlewiseSensorEntityDescription(
        key="bounce_mode",
        translation_key="bounce_mode",
        icon="mdi:arrow-up-down",
        value_fn=lambda c: c.bounce_mode,
    ),
    CradlewiseSensorEntityDescription(
        key="bounce_setting",
        translation_key="bounce_setting",
        icon="mdi:tune-variant",
        value_fn=lambda c: c.bounce_setting,
    ),
    CradlewiseSensorEntityDescription(
        key="bounce_amplitude",
        translation_key="bounce_amplitude",
        icon="mdi:sine-wave",
        value_fn=lambda c: c.bounce_amplitude,
    ),
    CradlewiseSensorEntityDescription(
        key="responsivity_setting",
        translation_key="responsivity_setting",
        icon="mdi:speedometer",
        value_fn=lambda c: c.responsivity_setting,
    ),
    CradlewiseSensorEntityDescription(
        key="music_mood",
        translation_key="music_mood",
        icon="mdi:music-note",
        value_fn=lambda c: c.music_mood,
    ),
    CradlewiseSensorEntityDescription(
        key="music_volume",
        translation_key="music_volume",
        icon="mdi:volume-medium",
        value_fn=lambda c: c.music_volume,
    ),
    CradlewiseSensorEntityDescription(
        key="music_mode",
        translation_key="music_mode",
        icon="mdi:playlist-music",
        value_fn=lambda c: c.music_mode,
    ),
    CradlewiseSensorEntityDescription(
        key="light_intensity",
        translation_key="light_intensity",
        icon="mdi:brightness-6",
        value_fn=lambda c: c.light_intensity,
    ),
    CradlewiseSensorEntityDescription(
        key="sleep_time",
        translation_key="sleep_time",
        icon="mdi:clock-outline",
        value_fn=lambda c: c.sleep_time,
    ),
    CradlewiseSensorEntityDescription(
        key="wake_up_time",
        translation_key="wake_up_time",
        icon="mdi:alarm",
        value_fn=lambda c: c.wake_up_time,
    ),
    CradlewiseSensorEntityDescription(
        key="firmware_version",
        translation_key="firmware_version",
        icon="mdi:chip",
        entity_registry_enabled_default=False,
        value_fn=lambda c: c.firmware_version,
    ),
)

ANALYTICS_DESCRIPTIONS: tuple[CradlewiseAnalyticsEntityDescription, ...] = (
    CradlewiseAnalyticsEntityDescription(
        key="total_sleep_today",
        translation_key="total_sleep_today",
        icon="mdi:sleep",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda a: a.total_sleep_minutes,
    ),
    CradlewiseAnalyticsEntityDescription(
        key="total_awake_today",
        translation_key="total_awake_today",
        icon="mdi:eye",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda a: a.total_awake_minutes,
    ),
    CradlewiseAnalyticsEntityDescription(
        key="nap_count",
        translation_key="nap_count",
        icon="mdi:counter",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda a: a.nap_count,
    ),
    CradlewiseAnalyticsEntityDescription(
        key="longest_nap",
        translation_key="longest_nap",
        icon="mdi:trophy",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda a: a.longest_nap_minutes,
    ),
    CradlewiseAnalyticsEntityDescription(
        key="soothe_count",
        translation_key="soothe_count",
        icon="mdi:hand-heart",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda a: a.total_soothe_count,
    ),
    CradlewiseAnalyticsEntityDescription(
        key="last_nap_start",
        translation_key="last_nap_start",
        icon="mdi:clock-start",
        value_fn=lambda a: a.last_nap_start,
    ),
    CradlewiseAnalyticsEntityDescription(
        key="last_nap_end",
        translation_key="last_nap_end",
        icon="mdi:clock-end",
        value_fn=lambda a: a.last_nap_end,
    ),
    CradlewiseAnalyticsEntityDescription(
        key="last_event",
        translation_key="last_event",
        icon="mdi:calendar-clock",
        value_fn=lambda a: a.last_event_value,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Cradlewise sensors."""
    coordinator: CradlewiseCoordinator = entry.runtime_data

    entities: list[SensorEntity] = []
    for cradle in coordinator.cradles.values():
        for desc in SENSOR_DESCRIPTIONS:
            entities.append(CradlewiseSensor(coordinator, cradle, desc))
        for desc in ANALYTICS_DESCRIPTIONS:
            entities.append(CradlewiseAnalyticsSensor(coordinator, cradle, desc))

    async_add_entities(entities)


def _device_info(cradle: CradlewiseCradle) -> dict[str, Any]:
    return {
        "identifiers": {(DOMAIN, cradle.cradle_id)},
        "name": f"Cradlewise {cradle.baby_name or 'Crib'}",
        "manufacturer": "Cradlewise",
        "model": "Smart Crib",
        "sw_version": cradle.firmware_version,
    }


class CradlewiseSensor(CoordinatorEntity[CradlewiseCoordinator], SensorEntity):
    entity_description: CradlewiseSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CradlewiseCoordinator,
        cradle: CradlewiseCradle,
        description: CradlewiseSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._cradle_id = cradle.cradle_id
        self._attr_unique_id = f"{cradle.cradle_id}_{description.key}"
        self._attr_device_info = _device_info(cradle)

    @property
    def native_value(self) -> Any:
        cradle = self.coordinator.cradles.get(self._cradle_id)
        if cradle is None:
            return None
        return self.entity_description.value_fn(cradle)

    @property
    def available(self) -> bool:
        return self.coordinator.cradles.get(self._cradle_id) is not None and super().available


class CradlewiseAnalyticsSensor(CoordinatorEntity[CradlewiseCoordinator], SensorEntity):
    entity_description: CradlewiseAnalyticsEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CradlewiseCoordinator,
        cradle: CradlewiseCradle,
        description: CradlewiseAnalyticsEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._cradle_id = cradle.cradle_id
        self._baby_id = cradle.baby_id
        self._attr_unique_id = f"{cradle.cradle_id}_{description.key}"
        self._attr_device_info = _device_info(cradle)

    @property
    def native_value(self) -> Any:
        if not self._baby_id:
            return None
        analytics = self.coordinator.analytics.get(self._baby_id)
        if analytics is None:
            return None
        return self.entity_description.value_fn(analytics)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.key != "last_event" or not self._baby_id:
            return None
        analytics = self.coordinator.analytics.get(self._baby_id)
        if analytics and analytics.last_event_time:
            return {"event_time": analytics.last_event_time}
        return None

    @property
    def available(self) -> bool:
        return self.coordinator.cradles.get(self._cradle_id) is not None and super().available
