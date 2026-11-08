"""One shared, bounded refresh per configured location; no AI inference calls."""
import asyncio
import logging
from datetime import timedelta
import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import BASE_URL

class FitzCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, logging.getLogger(__name__), name=entry.title,
                         update_interval=timedelta(minutes=5))
        self.entry = entry
        self.session = async_get_clientsession(hass)

    async def get(self, path, params=None):
        async with self.session.get(BASE_URL + path, params=params,
                                    timeout=aiohttp.ClientTimeout(total=25)) as response:
            response.raise_for_status()
            data = await response.json()
            if not isinstance(data, dict):
                raise ValueError("Unexpected Fitz response")
            return data

    async def _async_update_data(self):
        lat, lon = self.entry.data['latitude'], self.entry.data['longitude']
        try:
            weather = await self.get('/api/v1/weather', {'lat':lat, 'lon':lon})
            if not weather.get('hourly'):
                raise ValueError('No hourly forecast available')
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise UpdateFailed('Fitz weather is temporarily unavailable') from err
        packet = {'weather':weather}
        if 33.6 <= lat <= 34.15 and -97.1 <= lon <= -96.3:
            # Optional sources fail independently; never reuse an old reading as fresh.
            results = await asyncio.gather(
                self.get('/api/v1/regions/texoma'),
                self.get('/api/v1/lightning/reference'), return_exceptions=True)
            for key, value in zip(('lake','lightning'), results):
                if isinstance(value, dict):
                    packet[key] = value
        return packet
