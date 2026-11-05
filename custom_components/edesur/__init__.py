"""Set up Edesur account discovery and periodic updates."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EdesurApi
from .const import AUTH_GOOGLE, AUTH_PASSWORD, CONF_AUTH_METHOD, CONF_SOCIAL_ID, DOMAIN
from .coordinator import EdesurCoordinator
from .statistics import import_consumption_statistics

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Validate and initialize a configured Edesur account."""
    api = EdesurApi(async_get_clientsession(hass))
    auth_method = entry.data.get(CONF_AUTH_METHOD, AUTH_GOOGLE)
    if auth_method == AUTH_PASSWORD:
        credential = entry.data[CONF_PASSWORD]
    else:
        credential = entry.data[CONF_SOCIAL_ID]
    coordinator = EdesurCoordinator(
        hass, api, entry.data[CONF_EMAIL], credential, auth_method
    )
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    import_consumption_statistics(hass, coordinator.data)
    entry.async_on_unload(coordinator.async_add_listener(
        lambda: import_consumption_statistics(hass, coordinator.data)
    ))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Release in-memory state when the config entry is removed."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unloaded
