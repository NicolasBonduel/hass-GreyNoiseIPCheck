"""Config flow for GreyNoise IP Check integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, GREYNOISE_CHECK_URL

_LOGGER = logging.getLogger(__name__)


class GreyNoiseIPCheckConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GreyNoise IP Check."""

    VERSION = 1

    async def _test_connection(self) -> dict | None:
        """Test connectivity to the GreyNoise check API."""
        import json as json_lib

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                GREYNOISE_CHECK_URL,
                timeout=aiohttp.ClientTimeout(total=15),
                headers={
                    "User-Agent": "curl/8.0",
                    "Accept": "application/json",
                },
            ) as resp:
                if resp.status != 200:
                    _LOGGER.warning(
                        "GreyNoise API returned status %s", resp.status
                    )
                    return None
                body = await resp.text()
                try:
                    return json_lib.loads(body)
                except json_lib.JSONDecodeError:
                    _LOGGER.error(
                        "GreyNoise API returned non-JSON response"
                    )
        except Exception as err:  # noqa: BLE001
            _LOGGER.error(
                "Could not connect to GreyNoise check API: %s: %s",
                type(err).__name__,
                err,
            )
        return None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Verify we can reach the API
            data = await self._test_connection()
            if data is None:
                errors["base"] = "cannot_connect"
            else:
                # Ensure only one instance
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="GreyNoise IP Check",
                    data={},
                )

        return self.async_show_form(
            step_id="user",
            errors=errors,
        )
