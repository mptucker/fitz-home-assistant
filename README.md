# Fitz for Home Assistant

A HACS-style custom integration for Fitz weather and water data. Version 0.1.0.

## What you get

- A Home Assistant weather entity: hourly and twice-daily NWS forecasts via Fitz.
- Separate forecast temperature, wind, gusts, precipitation probability and summary sensors.
- Nearby observed feels-like, humidity, pressure in inches of mercury, and pressure trend.
- Active NWS alert count with alert headlines. An incomplete check is unavailable, never “no alerts.”
- Lake Texoma: USACE elevation, 24-hour change, release and conservation-pool fullness, plus Lighthouse-reference lightning status.
- A dashboard example with HA's native weather card and an embedded full Fitz view.

No Fitz login or API key is required. Add multiple locations by adding another integration entry. Setup defaults to Lake Texoma. Polling is shared across entities every five minutes; it does not trigger paid AI analysis. The weather entity's temperature and sky/wind are the current *hourly forecast*, not an observation. Nearby station readings are explicitly named observed. Missing/stale measurements become unavailable. The Lighthouse lightning sensor is fixed to the 25-mile Lighthouse reference and is not nationwide coverage. This is planning information, not rental clearance.

## Install manually now

1. Copy `custom_components/fitz` into your HA `/config/custom_components/fitz` directory.
2. Restart Home Assistant.
3. Settings → Devices & services → Add integration → **Fitz Weather**.
4. Enter a name and coordinates. Lake Texoma defaults are prefilled.
5. Add a Weather forecast card using the new weather entity. See `examples/dashboard.yaml` for more cards; actual entity IDs may differ.

## HACS installation

1. Open HACS → menu → Custom repositories.
2. Add `https://github.com/mptucker/fitz-home-assistant` with category **Integration**.
3. Search for **Fitz Weather**, download it, and restart Home Assistant.
4. Settings → Devices & services → Add integration → **Fitz Weather**.
5. Confirm Lake Texoma or enter your own U.S. coordinates.

This is a custom repository, not a listing in the HACS default catalog. The repository must be public for ordinary HACS installation.

## View the full app

Add a Webpage/iframe card with `https://wx.texomadestinations.com/wx/texoma` (staff lake view) or `https://wx.texomadestinations.com/app/` (general app). The full app and radar are interactive. Native HA sensors are available independently for histories and automations. There is no separate JavaScript dashboard dependency.

## Coverage and limits

Forecast coverage follows Fitz/NWS U.S. coverage. Lake measurements in this first integration are specifically Texoma; coastal/buoy entities are not implemented yet. Water temperature is not invented. Data depends on internet and provider availability. Do not use HA polling as an emergency warning delivery system. Configuration coordinates are sent to Fitz to fetch the forecast.

## Development checks

`python3 -m unittest discover -s tests` checks unit conversions, stale readings, missing data and alert-check behavior. `python3 -m compileall custom_components` checks syntax. Full Home Assistant setup/entity lifecycle and physical HA dashboard validation remain required before declaring production compatibility. No HA instance is bundled.
