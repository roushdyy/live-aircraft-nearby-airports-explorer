import requests
<<<<<<< HEAD

url = "https://opensky-network.org/api/states/all"

response = requests.get(url)

data = response.json()
=======
import csv
import os
from math import radians, sin, cos, sqrt, atan2

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

def geocode(city_name: str):
    """
    Convert a city name to its latitude and longitude.
    Returns: (latitude, longitude, full_city_name) or (None, None, None)
    """
    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    try:
        response = requests.get(GEOCODE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("results"):
            result = data["results"][0]
            return result["latitude"], result["longitude"], result["name"]
    except Exception as e:
        print(f"[Geocoding Error] {e}")
    return None, None, None
AIRPORTS_CSV_PATH = os.path.join("data", "airports.csv")

def load_airports():
    """Loads airport data from the CSV file into a list of dictionaries."""
    airports = []
    try:
        with open(AIRPORTS_CSV_PATH, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    lat = float(row.get("latitude_deg", 0))
                    lon = float(row.get("longitude_deg", 0))
                    if lat != 0 and lon != 0:
                        airports.append({
                            "name": row.get("name", "Unknown"),
                            "ident": row.get("ident", "N/A"),
                            "latitude_deg": lat,
                            "longitude_deg": lon,
                            "municipality": row.get("municipality", "N/A"),
                            "iso_country": row.get("iso_country", "N/A")
                        })
                except (ValueError, TypeError):
                    continue
    except FileNotFoundError:
        print(f"Error: airports.csv not found at {AIRPORTS_CSV_PATH}")
    return airports

def haversine(lat1, lon1, lat2, lon2):
    """Calculates the great-circle distance between two points in kilometers."""
    R = 6371.0  # Earth radius in km
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def find_nearest_airports(lat, lon, airports_data, limit=5):
    """Finds the nearest airports to a given coordinate."""
    airport_distances = []
    for airport in airports_data:
        try:
            distance = haversine(lat, lon, airport["latitude_deg"], airport["longitude_deg"])
            airport_distances.append((distance, airport))
        except Exception:
            continue
    airport_distances.sort(key=lambda x: x[0])
    return [airport for distance, airport in airport_distances[:limit]]
>>>>>>> 07ff805caedc8a63a41bd823c99df81766d72123
