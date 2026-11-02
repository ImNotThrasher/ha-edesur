"""Edesur sensors based on observed API response fields."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EdesurCoordinator


def _latest(data: Any, collection: str, date_key: str, fmt: str | None = None) -> dict[str, Any]:
    """Find the most recent dated item, independent of API ordering."""
    if not isinstance(data, dict) or not isinstance(data.get(collection), list):
        return {}
    items = [item for item in data[collection] if isinstance(item, dict)]
    def key(item: dict[str, Any]) -> str:
        raw = item.get(date_key)
        if not isinstance(raw, str):
            return ""
        try:
            return (datetime.strptime(raw, fmt) if fmt else datetime.fromisoformat(raw.replace("Z", "+00:00"))).date().isoformat()
        except ValueError:
            return ""
    return max(items, key=key, default={})


def _date(value: Any, fmt: str | None = None) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return (datetime.strptime(value, fmt) if fmt else datetime.fromisoformat(value.replace("Z", "+00:00"))).date()
    except ValueError:
        return None


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        result = Decimal(str(value))
        return float(result) if result.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


SENSORS = {
    "consumption": ("Último consumo", "readings", "readings", "readingDate", "activeConsumption", "number", "mdi:lightning-bolt"),
    "reading": ("Última lectura del medidor", "readings", "readings", "readingDate", "activeReading", "number", "mdi:counter"),
    "reading_date": ("Fecha de última lectura", "readings", "readings", "readingDate", "readingDate", "date_iso", "mdi:calendar"),
    "invoice_amount": ("Importe de última factura", "invoices", "invoices", "issueDate", "totalAmount", "money", "mdi:cash"),
    "invoice_date": ("Emisión de última factura", "invoices", "invoices", "issueDate", "issueDate", "date_local", "mdi:calendar"),
    "first_due": ("Primer vencimiento", "invoices", "invoices", "issueDate", "firstDueDate", "date_local", "mdi:calendar-clock"),
    "second_due": ("Segundo vencimiento", "invoices", "invoices", "issueDate", "secondDueDate", "date_local", "mdi:calendar-clock"),
    "payment_amount": ("Último pago", "payments", "payments", "paymentDate", "amount", "money", "mdi:cash-check"),
    "payment_date": ("Fecha del último pago", "payments", "payments", "paymentDate", "paymentDate", "date_iso", "mdi:calendar-check"),
    "agreement_status": ("Estado del convenio", "agreements", None, None, "current", "agreement", "mdi:file-document-check-outline"),
    "debt_status": ("Estado de deuda", "debts", None, None, "message", "debt", "mdi:cash-check"),
    "formality_status": ("Estado del último trámite", "formalities", "formalities", "openingDate", "statusDescription", "text", "mdi:clipboard-check-outline"),
    "formality_date": ("Fecha del último trámite", "formalities", "formalities", "openingDate", "openingDate", "date_iso", "mdi:calendar"),
    "supply_status": ("Estado del suministro", "supply_status", None, None, "status", "text", "mdi:transmission-tower"),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Expose contract sensors for every discovered account."""
    coordinator: EdesurCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [EdesurContractCount(coordinator, entry.entry_id)]
    for account in coordinator.data:
        entities.append(EdesurMeterNumber(coordinator, entry.entry_id, account))
        entities.extend(EdesurDataSensor(coordinator, entry.entry_id, account, key) for key in SENSORS)
    async_add_entities(entities)


class EdesurContractCount(CoordinatorEntity[EdesurCoordinator], SensorEntity):
    """Number of linked contracts."""

    _attr_has_entity_name = True
    _attr_name = "Suministros"
    _attr_icon = "mdi:transmission-tower"

    def __init__(self, coordinator: EdesurCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_contracts"

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data)


class EdesurAccountSensor(CoordinatorEntity[EdesurCoordinator], SensorEntity):
    """Base for a sensor associated with one electricity contract."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: EdesurCoordinator, entry_id: str, account: str) -> None:
        super().__init__(coordinator)
        self._account = account
        self._entry_id = entry_id

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._account)},
            name=f"Edesur {self._account}",
            manufacturer="Edesur",
        )


class EdesurMeterNumber(EdesurAccountSensor):
    """Meter identifier, retaining its original unique ID."""

    _attr_name = "Medidor"
    _attr_icon = "mdi:meter-electric"

    def __init__(self, coordinator: EdesurCoordinator, entry_id: str, account: str) -> None:
        super().__init__(coordinator, entry_id, account)
        self._attr_unique_id = f"{entry_id}_{account}_meter"

    @property
    def native_value(self) -> str | None:
        details = self.coordinator.data.get(self._account, {}).get("client")
        if not isinstance(details, dict):
            return None
        meter = details.get("meterNumber")
        return str(meter) if meter is not None else None


class EdesurDataSensor(EdesurAccountSensor):
    """Most recent reading, invoice, payment or supply status."""

    def __init__(self, coordinator: EdesurCoordinator, entry_id: str, account: str, key: str) -> None:
        super().__init__(coordinator, entry_id, account)
        self._key = key
        self._attr_unique_id = f"{entry_id}_{account}_{key}"
        name, _, _, _, _, kind, icon = SENSORS[key]
        self._attr_name = name
        self._attr_icon = icon
        if kind == "money":
            self._attr_native_unit_of_measurement = "ARS"
            self._attr_device_class = SensorDeviceClass.MONETARY
        elif kind.startswith("date"):
            self._attr_device_class = SensorDeviceClass.DATE
        elif key == "consumption":
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_device_class = SensorDeviceClass.ENERGY
            # Period consumption is not a monotonically increasing total.

    @property
    def native_value(self) -> float | date | str | None:
        _, section, collection, date_key, field, kind, _ = SENSORS[self._key]
        source = self.coordinator.data.get(self._account, {}).get(section)
        item = _latest(source, collection, date_key, "%d/%m/%Y" if section == "invoices" else None) if collection else source
        if not isinstance(item, dict):
            return None
        if kind == "agreement":
            if "current" not in item:
                return None
            current = item["current"]
            if current is None:
                return "Sin convenio vigente"
            if isinstance(current, dict):
                return str(current.get("state") or "Convenio registrado")
            return None
        if kind == "debt":
            if item.get("debts") is None and isinstance(item.get("message"), str) and "no posee deuda" in item["message"].casefold():
                return "Sin deuda registrada"
            if isinstance(item.get("debts"), list) and item["debts"]:
                return "Deuda registrada"
            return None
        raw = item.get(field)
        if kind in ("money", "number"):
            return _number(raw)
        if kind == "date_local":
            return _date(raw, "%d/%m/%Y")
        if kind == "date_iso":
            return _date(raw)
        return str(raw) if raw is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose minimal metadata; never publish invoice access tokens or private client data."""
        source = self.coordinator.data.get(self._account, {})
        if self._key.startswith("invoice") or self._key in ("first_due", "second_due"):
            item = _latest(source.get("invoices"), "invoices", "issueDate", "%d/%m/%Y")
            return {"invoice_number": item["number"]} if item.get("number") else {}
        if self._key == "consumption":
            records = source.get("readings")
            items = records.get("readings", []) if isinstance(records, dict) else []
            return {"history": [{"date": x["readingDate"][:10], "kwh": float(x["activeConsumption"])} for x in items if isinstance(x, dict) and isinstance(x.get("readingDate"), str) and _number(x.get("activeConsumption")) is not None][:36]}
        if self._key == "agreement_status":
            data = source.get("agreements")
            current = data.get("current") if isinstance(data, dict) else None
            if not isinstance(current, dict):
                return {}
            # Deliberately omit document URLs, barcodes and application numbers.
            return {k: current[k] for k in ("type", "numberInstallments", "openingDate", "closingDate") if current.get(k) is not None}
        if self._key == "formality_status":
            item = _latest(source.get("formalities"), "formalities", "openingDate")
            return {k: item[k] for k in ("caseNumber", "reason", "subReason") if item.get(k) is not None}
        if self._key.startswith("payment"):
            item = _latest(source.get("payments"), "payments", "paymentDate")
            return {k: item[k] for k in ("paymentTipe", "entity") if item.get(k) is not None}
        return {}
