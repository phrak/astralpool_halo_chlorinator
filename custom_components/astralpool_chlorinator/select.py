"""Platform for select integration."""
from __future__ import annotations

import logging
import asyncio

from .coordinator import ChlorinatorDataUpdateCoordinator

from homeassistant.components.select import (
    SelectEntity,
)
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from .models import ChlorinatorData
from .const import DOMAIN
from pychlorinator import chlorinator_parsers


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Chlorinator from a config entry."""
    data: ChlorinatorData = hass.data[DOMAIN][entry.entry_id]
    entities = [ChlorinatorSelect(data.coordinator)]
    async_add_entities(entities)


class ChlorinatorSelect(
    CoordinatorEntity[ChlorinatorDataUpdateCoordinator], SelectEntity
):
    """Representation of a Clorinator Select entity."""

    _attr_icon = "mdi:power"
    _attr_options = ["Off", "Auto", "Manual"]
    _attr_name = "Mode"
    _attr_unique_id = "pool01_mode_select"

    def __init__(
        self,
        coordinator: ChlorinatorDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo | None:
        return {
            "identifiers": {(DOMAIN, "POOL01")},
            "name": "POOL01",
            "model": "Viron eQuilibrium",
            "manufacturer": "Astral Pool",
        }

    @property
    def current_option(self):
        mode = self.coordinator.data.get("mode")
        if mode is chlorinator_parsers.Modes.Off:
            return "Off"
        elif mode is chlorinator_parsers.Modes.Auto:
            return "Auto"
        else:
            return "Manual"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option"""
        action: chlorinator_parsers.ChlorinatorActions.NoAction
        if option == "Off":
            action = chlorinator_parsers.ChlorinatorActions.Off
        elif option == "Auto":
            action = chlorinator_parsers.ChlorinatorActions.Auto
        elif option == "Manual":
            action = chlorinator_parsers.ChlorinatorActions.Manual
        else:
            action = chlorinator_parsers.ChlorinatorActions.NoAction

        await self.coordinator.chlorinator.async_write_action(action)
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()