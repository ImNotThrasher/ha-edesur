"""Sensors backed by validated contract discovery.

Avoid guessing units, monetary fields or dates until real API response
schemas are verified. Additional sensors can be introduced safely later.
"""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EdesurCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Create one account count sensor and one meter sensor per contract."""
    coordinator: EdesurCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [EdesurContractCount(coordinator, entry.entry_id)]
    entities.extend(EdesurMeterNumber(coordinator, entry.entry_id, account)
                    for account in coordinator.data)
    async_add_entities(entities)


class EdesurContractCount(CoordinatorEntity[EdesurCoordinator], SensorEntity):
    """Number of linked contracts returned by the API."""

    _attr_has_entity_name = True
    _attr_name = "Suministros"
    _attr_icon = "mdi:transmission-tower"

    def __init__(self, coordinator: EdesurCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_contracts"

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data)


class EdesurMeterNumber(CoordinatorEntity[EdesurCoordinator], SensorEntity):
    """Meter identifier, exposed only when get-client provides it."""

    _attr_has_entity_name = True
    _attr_name = "Medidor"
    _attr_icon = "mdi:meter-electric"

    def __init__(self, coordinator: EdesurCoordinator, entry_id: str, account: str) -> None:
        super().__init__(coordinator)
        self._account = account
        self._attr_unique_id = f"{entry_id}_{account}_meter"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._account)},
            name=f"Edesur {self._account}",
            manufacturer="Edesur",
        )

    @property
    def native_value(self) -> str | None:
        details = self.coordinator.data.get(self._account, {}).get("client")
        if not isinstance(details, dict):
            return None
        meter = details.get("meterNumber")
        return str(meter) if meter is not None else None
