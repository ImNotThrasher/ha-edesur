"""Basic unit tests for response validation (no live credentials)."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.edesur.api import EdesurApi, EdesurAuthError, EdesurConnectionError


@pytest.mark.asyncio
async def test_missing_token_rejected():
    api = EdesurApi(MagicMock())
    with pytest.raises(EdesurAuthError):
        await api.get_accounts("example@example.invalid")


@pytest.mark.asyncio
async def test_accounts_are_unique():
    api = EdesurApi(MagicMock())
    api._request = AsyncMock(return_value={"supplies": [
        {"contractAccount": "123"}, {"contractAccount": "123"},
        {"contractAccount": "456"}
    ]})
    assert await api.get_accounts("example@example.invalid") == ["123", "456"]


@pytest.mark.asyncio
async def test_invalid_account_schema_rejected():
    api = EdesurApi(MagicMock())
    api._request = AsyncMock(return_value={"unknown": []})
    with pytest.raises(EdesurConnectionError):
        await api.get_accounts("example@example.invalid")
