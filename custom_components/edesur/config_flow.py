"""Configuration flow for Edesur.

Only the Google/social method is implemented. Password-based login must not
be offered as working until its API behavior has been researched.
"""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector

from .api import EdesurApi, EdesurAuthError, EdesurError
from .const import AUTH_GOOGLE, CONF_AUTH_METHOD, CONF_SOCIAL_ID, DOMAIN


SOCIAL_ID_SELECTOR = selector.TextSelector(
    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
)


class EdesurConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Guide users through the currently supported login method."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return await self.async_step_google()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_AUTH_METHOD, default=AUTH_GOOGLE): vol.In({
                    AUTH_GOOGLE: "Google (social login)",
                }),
            }),
        )

    async def async_step_google(self, user_input=None):
        errors = {}
        if user_input is not None:
            email = user_input[CONF_EMAIL].strip().lower()
            social_id = user_input[CONF_SOCIAL_ID].strip()
            if not social_id.startswith("google_") or len(social_id) <= len("google_"):
                errors["base"] = "invalid_social_id"
                return self.async_show_form(
                    step_id="google",
                    data_schema=vol.Schema({vol.Required(CONF_EMAIL): str,
                                            vol.Required(CONF_SOCIAL_ID): SOCIAL_ID_SELECTOR}),
                    errors=errors,
                )
            api = EdesurApi(async_get_clientsession(self.hass))
            try:
                await api.login_google(email, social_id)
                accounts = await api.get_accounts(email)
                if not accounts:
                    errors["base"] = "no_accounts"
                else:
                    await self.async_set_unique_id(email)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Edesur ({email})",
                        data={CONF_AUTH_METHOD: AUTH_GOOGLE, CONF_EMAIL: email,
                              CONF_SOCIAL_ID: social_id},
                    )
            except EdesurAuthError:
                errors["base"] = "invalid_auth"
            except EdesurError:
                errors["base"] = "cannot_connect"
        return self.async_show_form(
            step_id="google",
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_SOCIAL_ID): SOCIAL_ID_SELECTOR,
            }),
            errors=errors,
        )
