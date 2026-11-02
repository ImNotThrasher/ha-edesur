"""Coordinate Edesur requests without exposing raw responses in logs."""
from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EdesurApi, EdesurAuthError, EdesurError
from .const import DOMAIN, UPDATE_INTERVAL


class EdesurCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Poll all contracts; reauthenticate on each cycle until token TTL is known."""

    def __init__(self, hass: HomeAssistant, api: EdesurApi, email: str, social_id: str) -> None:
        super().__init__(hass, logger=__import__("logging").getLogger(__name__),
                         name=DOMAIN, update_interval=UPDATE_INTERVAL)
        self.api = api
        self.email = email
        self.social_id = social_id

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        try:
            await self.api.login_google(self.email, self.social_id)
            accounts = await self.api.get_accounts(self.email)
            if not accounts:
                raise UpdateFailed("No linked contracts were returned")
            result: dict[str, dict[str, Any]] = {}
            for account in accounts:
                # Keep raw endpoint responses in memory for later validated
                # entity mappings; never write them to logs or diagnostics.
                client = await self.api.get_client(account)
                readings, invoices, payments, status = await asyncio.gather(
                    self.api.get_readings(account),
                    self.api.get_invoices(account),
                    self.api.get_payments(account),
                    self.api.get_supply_status(account),
                )
                # Optional endpoints must not break existing readings/invoices if unavailable.
                async def optional(fetch):
                    try:
                        return await fetch(account)
                    except EdesurError:
                        return None
                debts, formalities = await asyncio.gather(
                    optional(self.api.get_debts), optional(self.api.get_formalities)
                )
                result[account] = {
                    "client": client, "readings": readings,
                    "invoices": invoices, "payments": payments,
                    "supply_status": status,
                    "debts": debts, "formalities": formalities,
                }
            return result
        except EdesurAuthError as err:
            raise UpdateFailed("Edesur authentication failed") from err
        except EdesurError as err:
            raise UpdateFailed("Edesur API update failed") from err
