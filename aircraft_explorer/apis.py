import requests
import csv
import os
from math import radians, sin, cos, sqrt, atan2

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

def geocode(city_name):
    """Return (lat, lon, full_name) or (None, None, None)"""
    params = {"name": city_name, "count": 1, "format": "json"}
    try:
        resp = requests.get(GEOCODE_URL, params=params, timeout=10)
        data = resp.json()
        if data.get("results"):
            r = data["results"][0]
            return r["latitude"], r["longitude"], r["name"]
    except Exception as e:
        print("Geocoding error:", e)
    return None, None, None

def load_airports(csv_path="data/airports.csv"):
    """Load airports from CSV, return list of dicts with lat/lon"""
    airports = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    lat = float(row["latitude_deg"])
                    lon = float(row["longitude_deg"])
                    if lat != 0 or lon != 0:
                        airports.append({
                            "name": row["name"],
                            "ident": row["ident"],
                            "latitude_deg": lat,
                            "longitude_deg": lon,
                            "municipality": row.get("municipality", "")
                        })
                except:
                    continue
    except FileNotFoundError:
        print("airports.csv not found")
    return airports

def haversine(lat1, lon1, lat2, lon2):
    """Distance in km between two coordinates"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

def find_nearest_airports(lat, lon, airports, limit=5):
    """Return list of nearest airports (dicts)"""
    dist_list = []
    for apt in airports:
        d = haversine(lat, lon, apt["latitude_deg"], apt["longitude_deg"])
        dist_list.append((d, apt))
    dist_list.sort(key=lambda x: x[0])
    return [apt for _, apt in dist_list[:limit]]

def get_live_aircraft(lat_min, lon_min, lat_max, lon_max):
    """Fetch aircraft from OpenSky within bounding box"""
    url = "https://opensky-network.org/api/states/all"
    params = {"lamin": lat_min, "lomin": lon_min, "lamax": lat_max, "lomax": lon_max}
    try:
        resp = requests.get(url, params=params, timeout=15)
        data = resp.json()
        states = data.get("states", [])
        aircraft = []
        for s in states:
            # s[5]=lon, s[6]=lat, s[7]=altitude, s[9]=velocity
            if s[5] is not None and s[6] is not None:
                aircraft.append({
                    "callsign": (s[1] or "N/A").strip(),
                    "latitude": s[6],
                    "longitude": s[5],
                    "altitude": s[7] if s[7] else 0,
                    "velocity": s[9] if s[9] else 0
                })
        return aircraft
    except Exception as e:
        print("OpenSky error:", e)
        return []