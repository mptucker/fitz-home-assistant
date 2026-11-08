"""Configure each Fitz location through the Home Assistant UI."""
import asyncio
import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import BASE_URL, DOMAIN

class FitzConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            lat, lon = user_input['latitude'], user_input['longitude']
            await self.async_set_unique_id(f'{lat:.4f},{lon:.4f}')
            self._abort_if_unique_id_configured()
            try:
                async with async_get_clientsession(self.hass).get(
                    BASE_URL+'/api/v1/weather', params={'lat':lat,'lon':lon},
                    timeout=aiohttp.ClientTimeout(total=30)) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if not isinstance(data,dict) or not data.get('hourly'):
                        errors['base'] = 'no_forecast'
                    else:
                        return self.async_create_entry(title=user_input['name'], data=user_input)
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
                errors['base'] = 'cannot_connect'
        return self.async_show_form(step_id='user', data_schema=vol.Schema({
            vol.Required('name', default='Lake Texoma'):str,
            vol.Required('latitude', default=33.82):vol.All(vol.Coerce(float),vol.Range(min=18,max=72)),
            vol.Required('longitude', default=-96.65):vol.All(vol.Coerce(float),vol.Range(min=-180,max=-60)),
        }), errors=errors)
