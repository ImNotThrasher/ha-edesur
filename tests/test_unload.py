"""Regression tests for unloading the Edesur config entry.

The component module is loaded with minimal Home Assistant stubs so these
tests stay offline and don't require a running Home Assistant instance.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, Mock


ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "edesur"


class UnloadTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Import the integration with isolated minimal HA stubs."""
        self.saved_modules = {
            name: module for name, module in sys.modules.items()
            if name == "homeassistant" or name.startswith("homeassistant.")
            or name == "edesur" or name.startswith("edesur.")
        }

        def make_module(name, **attributes):
            module = types.ModuleType(name)
            module.__path__ = []
            module.__dict__.update(attributes)
            sys.modules[name] = module
            return module

        make_module("homeassistant")
        make_module("homeassistant.config_entries", ConfigEntry=object)
        make_module("homeassistant.const", Platform=types.SimpleNamespace(SENSOR="sensor"), CONF_EMAIL="email")
        make_module("homeassistant.core", HomeAssistant=object)
        make_module("homeassistant.helpers")
        make_module("homeassistant.helpers.aiohttp_client", async_get_clientsession=Mock())
        package = make_module("edesur")
        package.__path__ = [str(ROOT)]
        make_module("edesur.api", EdesurApi=object)
        make_module("edesur.const", CONF_SOCIAL_ID="social_id", DOMAIN="edesur")
        make_module("edesur.coordinator", EdesurCoordinator=object)
        make_module("edesur.statistics", import_consumption_statistics=Mock())

        spec = importlib.util.spec_from_file_location("edesur", ROOT / "__init__.py",
                                                      submodule_search_locations=[str(ROOT)])
        module = importlib.util.module_from_spec(spec)
        sys.modules["edesur"] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.integration = module

    async def asyncTearDown(self):
        for name in list(sys.modules):
            if name == "homeassistant" or name.startswith("homeassistant.") or name == "edesur" or name.startswith("edesur."):
                del sys.modules[name]
        sys.modules.update(self.saved_modules)

    async def test_unload_success_cleans_data_without_manual_callback_call(self):
        entry = types.SimpleNamespace(entry_id="test-entry")
        hass = types.SimpleNamespace(
            config_entries=types.SimpleNamespace(async_unload_platforms=AsyncMock(return_value=True)),
            data={"edesur": {"test-entry": object(), "other-entry": object()}},
        )

        self.assertTrue(await self.integration.async_unload_entry(hass, entry))
        hass.config_entries.async_unload_platforms.assert_awaited_once_with(entry, ["sensor"])
        self.assertNotIn("test-entry", hass.data["edesur"])
        self.assertIn("other-entry", hass.data["edesur"])

    async def test_unload_failure_preserves_data(self):
        entry = types.SimpleNamespace(entry_id="test-entry")
        coordinator = object()
        hass = types.SimpleNamespace(
            config_entries=types.SimpleNamespace(async_unload_platforms=AsyncMock(return_value=False)),
            data={"edesur": {"test-entry": coordinator}},
        )

        self.assertFalse(await self.integration.async_unload_entry(hass, entry))
        self.assertIs(hass.data["edesur"]["test-entry"], coordinator)


if __name__ == "__main__":
    unittest.main()
