"""Set up Edesur account discovery and periodic updates."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EdesurApi
from .const import CONF_SOCIAL_ID, DOMAIN
from .coordinator import EdesurCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Validate and initialize a configured Edesur account."""
    api = EdesurApi(async_get_clientsession(hass))
    coordinator = EdesurCoordinator(
        hass, api, entry.data[CONF_EMAIL], entry.data[CONF_SOCIAL_ID]
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Release in-memory state when the config entry is removed."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
