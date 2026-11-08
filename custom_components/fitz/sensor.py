from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from .data import values
from .entity import FitzEntity

SENSORS = {
 'forecast_temperature':('Hourly forecast temperature','°F',SensorDeviceClass.TEMPERATURE),
 'forecast_wind':('Hourly forecast wind','mph',SensorDeviceClass.WIND_SPEED),
 'forecast_gust':('Hourly forecast gust','mph',SensorDeviceClass.WIND_SPEED),
 'rain_probability':('Hourly rain probability','%',None),
 'humidity':('Observed humidity','%',SensorDeviceClass.HUMIDITY),
 'pressure':('Observed pressure','inHg',SensorDeviceClass.PRESSURE),
 'pressure_trend':('Pressure trend',None,None),
 'feels_like':('Observed feels like','°F',SensorDeviceClass.TEMPERATURE),
 'active_alerts':('Active NWS alerts',None,None),
 'condition':('Hourly forecast summary',None,None),
 'lake_elevation':('Lake elevation','ft',None),
 'lake_change':('Lake change over 24h','ft',None),
 'lake_release':('Reservoir release','ft³/s',None),
 'lake_full':('Conservation pool full','%',None),
 'lightning_status':('Lighthouse lightning',None,None),
}

async def async_setup_entry(hass, entry, async_add_entities):
    c=entry.runtime_data
    texoma=33.6<=entry.data['latitude']<=34.15 and -97.1<=entry.data['longitude']<=-96.3
    async_add_entities(FitzSensor(c,key,*desc) for key,desc in SENSORS.items()
                       if texoma or not key.startswith(('lake_','lightning_')))

class FitzSensor(FitzEntity, SensorEntity):
    def __init__(self, coordinator, key, name, unit, device_class):
        super().__init__(coordinator,key)
        self.key=key;self._attr_name=name;self._attr_native_unit_of_measurement=unit
        self._attr_device_class=device_class
        if unit:self._attr_state_class=SensorStateClass.MEASUREMENT

    @property
    def native_value(self):return values(self.coordinator.data).get(self.key)

    @property
    def available(self):return super().available and self.native_value is not None

    @property
    def extra_state_attributes(self):
        w=self.coordinator.data.get('weather',{})
        if self.key.startswith('lake_'):
            lake=self.coordinator.data.get('lake',{})
            return {'source':lake.get('source'), 'provisional':lake.get('provisional'), 'datum':'See source; elevation is not depth'}
        if self.key=='active_alerts':
            return {'alerts':[{'event':a.get('event'),'headline':a.get('headline'),'expires':a.get('expires')} for a in w.get('alerts',[])], 'check_state':w.get('alertStatus',{}).get('state')}
        return {'forecast_issued':w.get('issuedAt'),'forecast_valid':(w.get('hourly') or [{}])[0].get('startTime'),
                'station':(w.get('surfaceObservations') or {}).get('station')}
