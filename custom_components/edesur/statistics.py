"""Import Edesur billing-period readings as external long-term statistics.

Each observation belongs to its reading date, not a calendar-month energy total.
The mean series supports native statistics graphs without inventing hourly usage.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from homeassistant.components.recorder.statistics import (
    StatisticMeanType,
    async_add_external_statistics,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def import_consumption_statistics(hass: HomeAssistant, data: dict) -> None:
    """Upsert dated provider observations; never fabricate intermediate readings."""
    if "recorder" not in hass.config.components:
        return

    for account, payload in data.items():
        readings = payload.get("readings")
        items = readings.get("readings", []) if isinstance(readings, dict) else []
        if not isinstance(items, list):
            continue

        by_hour = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            raw_date = item.get("readingDate")
            raw_value = item.get("activeConsumption")
            if not isinstance(raw_date, str) or isinstance(raw_value, bool):
                continue
            try:
                day = datetime.fromisoformat(raw_date.replace("Z", "+00:00")).date()
                amount = Decimal(str(raw_value))
                if not amount.is_finite() or amount < 0:
                    continue
                # Noon UTC avoids midnight timezone shifts in Argentina.
                start = datetime(day.year, day.month, day.day, 12, tzinfo=timezone.utc)
                by_hour[start] = float(amount)
            except (ValueError, TypeError, InvalidOperation, OverflowError):
                continue

        if not by_hour:
            continue

        metadata = {
            "statistic_id": f"{DOMAIN}:consumption_{account}",
            "source": DOMAIN,
            "name": f"Edesur {account} - consumo por lectura",
            "unit_of_measurement": "kWh",
            "unit_class": "energy",
            "mean_type": StatisticMeanType.ARITHMETIC,
            "has_sum": False,
        }
        statistics = [
            {"start": start, "mean": value, "min": value, "max": value}
            for start, value in sorted(by_hour.items())
        ]
        try:
            # Recorder upserts an existing statistic with the same start timestamp.
            async_add_external_statistics(hass, metadata, statistics)
        except (ValueError, RuntimeError) as err:
            _LOGGER.warning("Could not import Edesur consumption statistics: %s", type(err).__name__)
