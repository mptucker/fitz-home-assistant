from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

class FitzEntity(CoordinatorEntity):
    _attr_has_entity_name = True
    _attr_attribution = 'Weather and water data via Fitz · NWS / NOAA / USACE'

    def __init__(self, coordinator, key):
        super().__init__(coordinator)
        entry=coordinator.entry
        self._attr_unique_id = f'{entry.unique_id}_{key}'
        self._attr_device_info = {'identifiers':{(DOMAIN,entry.unique_id)},'name':entry.title,
                                 'manufacturer':'Fitz','model':'Weather and water intelligence',
                                 'configuration_url':'https://wx.texomadestinations.com/app/'}
