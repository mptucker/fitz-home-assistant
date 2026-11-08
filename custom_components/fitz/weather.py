"""NWS forecast conditions through Fitz, explicitly not station observations."""
from homeassistant.components.weather import WeatherEntity, WeatherEntityFeature
from homeassistant.const import UnitOfTemperature, UnitOfSpeed, UnitOfPressure
from .data import condition, fahrenheit, wind, values
from .entity import FitzEntity

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([FitzWeather(entry.runtime_data)])

class FitzWeather(FitzEntity, WeatherEntity):
    _attr_name = 'Forecast'
    _attr_native_temperature_unit = UnitOfTemperature.FAHRENHEIT
    _attr_native_wind_speed_unit = UnitOfSpeed.MILES_PER_HOUR
    _attr_native_pressure_unit = UnitOfPressure.INHG
    _attr_supported_features = WeatherEntityFeature.FORECAST_HOURLY | WeatherEntityFeature.FORECAST_TWICE_DAILY

    def __init__(self, coordinator):super().__init__(coordinator,'weather')
    @property
    def period(self):return self.coordinator.data['weather']['hourly'][0]
    @property
    def condition(self):return condition(self.period)
    @property
    def native_temperature(self):return fahrenheit(self.period)
    @property
    def native_wind_speed(self):return wind(self.period.get('windSpeed'))
    @property
    def native_wind_gust_speed(self):return self.period.get('gustMph')
    @property
    def wind_bearing(self):return self.period.get('windDirection')
    @property
    def humidity(self):return values(self.coordinator.data).get('humidity')
    @property
    def native_pressure(self):return values(self.coordinator.data).get('pressure')

    def forecasts(self,key):
        return [{'datetime':p['startTime'],'condition':condition(p),
                 'native_temperature':fahrenheit(p),'native_wind_speed':wind(p.get('windSpeed')),
                 'native_wind_gust_speed':p.get('gustMph'),'wind_bearing':p.get('windDirection'),
                 'precipitation_probability':(p.get('probabilityOfPrecipitation') or {}).get('value'),
                 **({'is_daytime':p.get('isDaytime',True)} if key=='daily' else {})}
                for p in self.coordinator.data['weather'].get(key,[]) if p.get('startTime')]

    async def async_forecast_hourly(self):return self.forecasts('hourly')
    async def async_forecast_twice_daily(self):return self.forecasts('daily')
