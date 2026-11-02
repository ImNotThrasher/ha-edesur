"""Offline API validation tests, without Home Assistant runtime or pytest."""
from pathlib import Path
import importlib.util
import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "edesur"
PACKAGE = "edesur"
if PACKAGE not in sys.modules:
    pkg = types.ModuleType(PACKAGE)
    pkg.__path__ = [str(ROOT)]
    sys.modules[PACKAGE] = pkg
if PACKAGE + ".const" not in sys.modules:
    spec = importlib.util.spec_from_file_location(PACKAGE + ".const", ROOT / "const.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
if PACKAGE + ".api" not in sys.modules:
    spec = importlib.util.spec_from_file_location(PACKAGE + ".api", ROOT / "api.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

from edesur.api import EdesurApi, EdesurAuthError, EdesurConnectionError


class ApiValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_token_rejected(self):
        client = EdesurApi(MagicMock())
        with self.assertRaises(EdesurAuthError):
            await client.get_accounts("example@example.invalid")

    async def test_accounts_are_unique(self):
        client = EdesurApi(MagicMock())
        client._request = AsyncMock(return_value={"supplies": [
            {"contractAccount": "123"}, {"contractAccount": "123"},
            {"contractAccount": "456"}
        ]})
        self.assertEqual(await client.get_accounts("example@example.invalid"), ["123", "456"])

    async def test_invalid_account_schema_rejected(self):
        client = EdesurApi(MagicMock())
        client._request = AsyncMock(return_value={"unknown": []})
        with self.assertRaises(EdesurConnectionError):
            await client.get_accounts("example@example.invalid")


if __name__ == "__main__":
    unittest.main()
