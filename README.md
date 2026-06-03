# Live Aircraft Nearby Airports Explorer

A Flask web app that finds nearby airports for a searched city, displays live aircraft tracking on a map, and stores saved records in SQLite.

## Features

- Search for a city and find nearby airports
- Display live aircraft positions from OpenSky Network
- Show interactive map markers for airports and aircraft
- Save airport bookmarks
- Save aircraft snapshots and review recent activity
- Compare current live traffic against a saved snapshot
- Store history, bookmarks, and snapshots in SQLite

## APIs used

- Open-Meteo geocoding API for city search
- OpenSky Network API for live aircraft state data
- OurAirports CSV data API for airport location data

## Installation

1. Clone the repository:

```bash
git clone <repo-url>
cd live-aircraft-nearby-airports-explorer
```

2. Create and activate your Python environment:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# or
source venv/bin/activate # macOS / Linux
```

3. Install dependencies:

```bash
pip install flask requests folium matplotlib
```

## Running the app

```bash
cd aircraft_explorer
python app.py
```

Open your browser at `http://127.0.0.1:5001/`.

## Project structure

- `aircraft_explorer/app.py` - Flask app routes and view rendering
- `aircraft_explorer/apis.py` - external API calls and airport lookup
- `aircraft_explorer/map_utils.py` - map creation with Folium
- `aircraft_explorer/charts.py` - altitude chart generation with Matplotlib
- `aircraft_explorer/control_panel.py` - SQLite helpers for history, bookmarks, snapshots, and comparison
- `aircraft_explorer/templates/` - HTML templates
- `aircraft_explorer/static/` - static assets like CSS and generated chart images

## Notes

- A SQLite database file is created automatically in the `aircraft_explorer` folder.
- Use the control panel to view saved bookmarks, recent snapshots, and traffic comparisons.

- Uses the Open-Meteo geocoding API for city lookup
- Uses the OpenSky Network API for live aircraft data
- Uses the OurAirports data API for airport location data
