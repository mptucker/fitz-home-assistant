"""Pure conversions. Missing or stale data is never translated to zero."""
import math
import re
from datetime import datetime, timezone

def number(value):
    return value if isinstance(value,(float,int)) and not isinstance(value,bool) and math.isfinite(value) else None

def fresh(record, max_age=5400):
    if not record or record.get('stale'):
        return False
    try:
        age=(datetime.now(timezone.utc)-datetime.fromisoformat(record['observedAt'].replace('Z','+00:00'))).total_seconds()
        return -60 <= age <= max_age
    except (KeyError,ValueError,TypeError):
        return False

def wind(value):
    values=[float(v) for v in re.findall(r'\d+(?:\.\d+)?', value or '')]
    return max(values) if values else None

def fahrenheit(period):
    value=number(period.get('temperature'))
    if value is None:return None
    return value*1.8+32 if period.get('temperatureUnit')=='C' else value

def condition(period):
    text=(period.get('shortForecast') or '').lower()
    for words,result in ((('thunder',),'lightning-rainy'),(('sleet','freezing'),'snowy-rainy'),(('snow',),'snowy'),(('rain','shower'),'rainy'),(('fog','haze'),'fog'),(('partly','mostly sunny','mostly clear'),'partlycloudy'),(('cloud','overcast'),'cloudy'),(('clear','sunny'),'sunny')):
        if any(word in text for word in words):
            return 'clear-night' if result=='sunny' and period.get('isDaytime') is False else result
    return None

def values(packet):
    weather=packet.get('weather',{});hours=weather.get('hourly') or []
    current=hours[0] if hours else {};surface=weather.get('surfaceObservations') or {}
    result={'forecast_temperature':fahrenheit(current), 'forecast_wind':wind(current.get('windSpeed')),
            'forecast_gust':number(current.get('gustMph')),
            'rain_probability':number((current.get('probabilityOfPrecipitation') or {}).get('value')),
            'condition':current.get('shortForecast')}
    for key,source in [('humidity','humidity'),('pressure','pressure'),('feels_like','feelsLike')]:
        record=surface.get(source) or {}
        result[key]=number(record.get('value')) if fresh(record) else None
    pressure=surface.get('pressure') or {}
    result['pressure_trend']=(pressure.get('trend') or {}).get('direction') if fresh(pressure) else None
    alert=weather.get('alertStatus',{})
    result['active_alerts']=len(weather.get('alerts',[])) if alert.get('state')=='ready' else None
    for key,source in [('lake_elevation','elevation'),('lake_release','release'),('lake_full','conservation')]:
        record=(packet.get('lake',{}).get('metrics') or {}).get(source,{})
        result[key]=number(record.get('value')) if fresh(record,43200) else None
    record=(packet.get('lake',{}).get('metrics') or {}).get('elevation',{})
    result['lake_change']=number(record.get('change24h')) if fresh(record,43200) else None
    lightning=packet.get('lightning',{}).get('lightningStatus') or {}
    stamp=lightning.get('checkedAt')
    result['lightning_status']=lightning.get('label') if isinstance(stamp,(int,float)) and 0<=datetime.now(timezone.utc).timestamp()-stamp<240 else None
    return result
