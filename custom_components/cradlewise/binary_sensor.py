"""Binary sensor entities for Cradlewise."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pycradlewise import CradlewiseCradle

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CradlewiseCoordinator
from .sensor import _device_info


@dataclass(frozen=True, kw_only=True)
class CradlewiseBinarySensorEntityDescription(BinarySensorEntityDescription):
    value_fn: Callable[[CradlewiseCradle], bool | None]


BINARY_SENSOR_DESCRIPTIONS: tuple[CradlewiseBinarySensorEntityDescription, ...] = (
    CradlewiseBinarySensorEntityDescription(
        key="online",
        translation_key="online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda c: c.online,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="baby_present",
        translation_key="baby_present",
        device_class=BinarySensorDeviceClass.OCCUPANCY,
        icon="mdi:baby-face-outline",
        value_fn=lambda c: c.baby_present,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="baby_needs_attention",
        translation_key="baby_needs_attention",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:alert-circle-outline",
        value_fn=lambda c: c.baby_needs_attention,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="baby_needs_help",
        translation_key="baby_needs_help",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:alert",
        value_fn=lambda c: c.baby_needs_help,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="crib_helping",
        translation_key="crib_helping",
        icon="mdi:hand-heart",
        value_fn=lambda c: c.is_crib_helping,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="bouncing",
        translation_key="bouncing",
        icon="mdi:arrow-up-down-bold",
        value_fn=lambda c: c.bouncing,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="music_playing",
        translation_key="music_playing",
        icon="mdi:music",
        value_fn=lambda c: c.music_playing,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="light_on",
        translation_key="light_on",
        icon="mdi:lightbulb",
        value_fn=lambda c: c.light_on,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="loud_sound_detected",
        translation_key="loud_sound_detected",
        device_class=BinarySensorDeviceClass.SOUND,
        icon="mdi:volume-high",
        value_fn=lambda c: c.loud_sound_detected,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="inside_sleep_schedule",
        translation_key="inside_sleep_schedule",
        icon="mdi:calendar-clock",
        value_fn=lambda c: c.inside_sleep_schedule,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="inside_soothing_window",
        translation_key="inside_soothing_window",
        icon="mdi:clock-check",
        value_fn=lambda c: c.inside_soothing_window,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="rocking_not_effective",
        translation_key="rocking_not_effective",
        icon="mdi:alert-outline",
        value_fn=lambda c: c.rocking_not_effective,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="charging",
        translation_key="charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=lambda c: c.charging,
    ),
    CradlewiseBinarySensorEntityDescription(
        key="power_supply_removed",
        translation_key="power_supply_removed",
        device_class=BinarySensorDeviceClass.PLUG,
        value_fn=lambda c: not c.supply_removed if c.supply_removed is not None else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: CradlewiseCoordinator = entry.runtime_data

    entities: list[CradlewiseBinarySensor] = []
    for cradle in coordinator.cradles.values():
        for desc in BINARY_SENSOR_DESCRIPTIONS:
            entities.append(CradlewiseBinarySensor(coordinator, cradle, desc))

    async_add_entities(entities)


class CradlewiseBinarySensor(
    CoordinatorEntity[CradlewiseCoordinator], BinarySensorEntity
):
    entity_description: CradlewiseBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CradlewiseCoordinator,
        cradle: CradlewiseCradle,
        description: CradlewiseBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._cradle_id = cradle.cradle_id
        self._attr_unique_id = f"{cradle.cradle_id}_{description.key}"
        self._attr_device_info = _device_info(cradle)

    @property
    def is_on(self) -> bool | None:
        cradle = self.coordinator.cradles.get(self._cradle_id)
        if cradle is None:
            return None
        return self.entity_description.value_fn(cradle)

    @property
    def available(self) -> bool:
        return self.coordinator.cradles.get(self._cradle_id) is not None and super().available
