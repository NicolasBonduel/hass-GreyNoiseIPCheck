"""Data update coordinator for GreyNoise IP Check."""

from __future__ import annotations

from datetime import timedelta, datetime, timezone
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL_HOURS, DOMAIN, GREYNOISE_CHECK_URL

_LOGGER = logging.getLogger(__name__)


class GreyNoiseDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator to fetch GreyNoise IP check data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=DEFAULT_SCAN_INTERVAL_HOURS),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from the GreyNoise check API."""
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                GREYNOISE_CHECK_URL,
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": "curl/8.0",
                    "Accept": "application/json",
                },
            ) as resp:
                if resp.status != 200:
                    raise UpdateFailed(
                        f"GreyNoise API returned HTTP {resp.status}"
                    )
                data = await resp.json(content_type=None)
                data["_last_checked"] = datetime.now(timezone.utc).isoformat()
                _LOGGER.debug("GreyNoise check response: %s", data)
                return data
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with GreyNoise: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed("Timeout connecting to GreyNoise API") from err
        except ValueError as err:
            raise UpdateFailed(f"Invalid response from GreyNoise API: {err}") from err
