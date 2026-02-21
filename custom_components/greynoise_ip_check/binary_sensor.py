"""Binary sensor platform for GreyNoise IP Check."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CLASSIFICATION,
    ATTR_COMMON_BUSINESS,
    ATTR_ERROR,
    ATTR_IP,
    ATTR_LAST_CHECKED,
    ATTR_NOISE,
    ATTR_STATUS,
    ATTR_TRUST_LEVEL,
    DOMAIN,
)
from .coordinator import GreyNoiseDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GreyNoise IP Check binary sensor from a config entry."""
    coordinator: GreyNoiseDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GreyNoiseIPCleanBinarySensor(coordinator, entry)])


class GreyNoiseIPCleanBinarySensor(
    CoordinatorEntity[GreyNoiseDataUpdateCoordinator], BinarySensorEntity
):
    """Binary sensor that indicates whether the IP is clean."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_device_class = BinarySensorDeviceClass.SAFETY

    def __init__(
        self,
        coordinator: GreyNoiseDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="GreyNoise IP Check",
            manufacturer="GreyNoise Intelligence",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://check.labs.greynoise.io/",
        )

    @property
    def is_on(self) -> bool | None:
        """Return True if the IP has been flagged (unsafe).

        SAFETY device class: on = Unsafe, off = Safe.
        """
        if self.coordinator.data is None:
            return None
        # on (unsafe) when noise is detected
        return self.coordinator.data.get("noise", False)

    @property
    def icon(self) -> str:
        """Return icon based on state."""
        if self.is_on:
            return "mdi:shield-alert"
        return "mdi:shield-check"

    @property
    def extra_state_attributes(self) -> dict[str, str | bool | None]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}
        data = self.coordinator.data
        return {
            ATTR_IP: data.get("ip"),
            ATTR_STATUS: data.get("status"),
            ATTR_CLASSIFICATION: data.get("classification"),
            ATTR_NOISE: data.get("noise"),
            ATTR_COMMON_BUSINESS: data.get("common_business_services"),
            ATTR_TRUST_LEVEL: data.get("trust_level"),
            ATTR_ERROR: data.get("error"),
            ATTR_LAST_CHECKED: data.get("_last_checked"),
        }
