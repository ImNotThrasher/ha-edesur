"""Offline tests for Edesur API and consumption-statistics importer."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "edesur"
PACKAGE = "edesur"
package = types.ModuleType(PACKAGE)
package.__path__ = [str(ROOT)]
sys.modules.setdefault(PACKAGE, package)


def load(name):
    spec = importlib.util.spec_from_file_location(PACKAGE + "." + name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


load("const")
api = load("api")


class Response:
    def __init__(self, status, data):
        self.status, self.data = status, data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def json(self, **kwargs):
        return self.data


class Session:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return next(self.responses)


class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_social_login_payload_and_account_discovery(self):
        session = Session([
            Response(200, {"email": "demo@example.com", "token": "secret"}),
            Response(200, {"supplies": [
                {"contractAccount": "100"}, {"contractAccount": "200"},
                {"contractAccount": "100"}]}),
        ])
        client = api.EdesurApi(session)
        await client.login_google("demo@example.com", "google_FAKE")
        self.assertEqual(session.calls[0][2]["json"], {
            "socialMediaEmail": "demo@example.com", "socialMediaId": "google_FAKE"})
        self.assertEqual(await client.get_accounts("demo@example.com"), ["100", "200"])
        self.assertEqual(session.calls[1][2]["headers"]["Authorization"], "Bearer secret")

    async def test_social_login_rejects_mismatched_account(self):
        client = api.EdesurApi(Session([Response(200, {"email": "other@example.com", "token": "x"})]))
        with self.assertRaises(api.EdesurAuthError):
            await client.login_google("demo@example.com", "google_FAKE")

    async def test_api_rejects_http_errors(self):
        client = api.EdesurApi(Session([Response(503, {})]))
        with self.assertRaises(api.EdesurConnectionError):
            await client.login_google("demo@example.com", "google_FAKE")


class StatisticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ha = types.ModuleType("homeassistant")
        ha.__path__ = []
        components = types.ModuleType("homeassistant.components")
        components.__path__ = []
        recorder = types.ModuleType("homeassistant.components.recorder")
        recorder.__path__ = []
        statistics = types.ModuleType("homeassistant.components.recorder.statistics")
        statistics.StatisticMeanType = types.SimpleNamespace(ARITHMETIC="arithmetic")
        statistics.async_add_external_statistics = Mock()
        core = types.ModuleType("homeassistant.core")
        core.HomeAssistant = object
        for name, mod in [
            ("homeassistant", ha), ("homeassistant.components", components),
            ("homeassistant.components.recorder", recorder),
            ("homeassistant.components.recorder.statistics", statistics),
            ("homeassistant.core", core),
        ]:
            sys.modules.setdefault(name, mod)
        cls.stats = load("statistics")

    def test_imports_dated_readings_without_fabricated_hours(self):
        hass = Mock()
        hass.config.components = {"recorder"}
        readings = {"readings": [
            {"readingDate": "2026-09-03", "activeConsumption": 184},
            {"readingDate": "2026-10-04", "activeConsumption": 11},
            {"readingDate": "2026-10-05", "activeConsumption": -2},
            {"readingDate": "invalid", "activeConsumption": 3},
        ]}
        with patch.object(self.stats, "async_add_external_statistics") as add:
            self.stats.import_consumption_statistics(hass, {"123": {"readings": readings}})
        add.assert_called_once()
        metadata, points = add.call_args.args[1:]
        self.assertEqual(metadata["statistic_id"], "edesur:consumption_123")
        self.assertEqual([x["mean"] for x in points], [184.0, 11.0])
        self.assertTrue(all(x["start"].hour == 12 for x in points))

    def test_missing_recorder_skips_import(self):
        hass = Mock()
        hass.config.components = set()
        with patch.object(self.stats, "async_add_external_statistics") as add:
            self.stats.import_consumption_statistics(hass, {"123": {"readings": {}}})
        add.assert_not_called()


if __name__ == "__main__":
    unittest.main()
