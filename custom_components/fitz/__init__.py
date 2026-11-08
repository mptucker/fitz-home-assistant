"""Fitz weather and water intelligence."""
from .const import PLATFORMS
from .coordinator import FitzCoordinator

async def async_setup_entry(hass, entry):
    coordinator = FitzCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
