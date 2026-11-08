import importlib.util
from pathlib import Path
import unittest
from datetime import datetime, timezone, timedelta
spec=importlib.util.spec_from_file_location('fitz_data',Path(__file__).parents[1]/'custom_components/fitz/data.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class DataTests(unittest.TestCase):
    def test_missing_not_zero(self):
        values=m.values({'weather':{'hourly':[],'alerts':[],'alertStatus':{'state':'checking'}}})
        self.assertIsNone(values['active_alerts']);self.assertIsNone(values['pressure']);self.assertIsNone(values['lake_elevation'])
    def test_alerts_only_ready(self):
        self.assertEqual(m.values({'weather':{'alerts':[],'alertStatus':{'state':'ready'}}})['active_alerts'],0)
    def test_units(self):
        self.assertEqual(m.fahrenheit({'temperature':20,'temperatureUnit':'C'}),68)
        self.assertEqual(m.wind('5 to 10 mph'),10)
        self.assertIsNone(m.wind('Unavailable'))
    def test_stale_reading_not_reported(self):
        now=datetime.now(timezone.utc)
        record={'value':30.1,'observedAt':(now-timedelta(hours=3)).isoformat()}
        self.assertIsNone(m.values({'weather':{'surfaceObservations':{'pressure':record}}})['pressure'])
        record['observedAt']=now.isoformat()
        self.assertEqual(m.values({'weather':{'surfaceObservations':{'pressure':record}}})['pressure'],30.1)
    def test_condition(self):
        self.assertEqual(m.condition({'shortForecast':'Clear','isDaytime':False}),'clear-night')
        self.assertEqual(m.condition({'shortForecast':'Thunderstorms likely'}),'lightning-rainy')
        self.assertIsNone(m.condition({'shortForecast':'Unknown'}))
if __name__=='__main__':unittest.main()
