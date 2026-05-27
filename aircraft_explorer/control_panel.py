import sqlite3
import os
from typing import List, Dict

DB = os.path.join(os.path.dirname(__file__), "aircraft.db")

def connect():
    return sqlite3.connect(DB)

# -------- Search history --------
def save_search(city, lat, lon):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO searches (city, latitude, longitude) VALUES (?,?,?)", (city, lat, lon))
    conn.commit()
    conn.close()

def get_searches(limit=20):
    conn = connect()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, city, latitude, longitude, timestamp FROM searches ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_search(search_id):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM searches WHERE id = ?", (search_id,))
    conn.commit()
    conn.close()

# -------- Bookmarked airports --------
def save_bookmark(name, icao, lat, lon):
    conn = connect()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO saved_airports (airport_name, icao, latitude, longitude) VALUES (?,?,?,?)", (name, icao, lat, lon))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # already exists
    finally:
        conn.close()

def get_bookmarks():
    conn = connect()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, airport_name, icao, latitude, longitude, saved_time FROM saved_airports ORDER BY saved_time DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_bookmark(bookmark_id):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM saved_airports WHERE id = ?", (bookmark_id,))
    conn.commit()
    conn.close()

# -------- Aircraft snapshots --------
def save_snapshots(aircraft_list):
    """Save multiple aircraft records (each as one row)"""
    if not aircraft_list:
        return
    conn = connect()
    c = conn.cursor()
    data = [(a["callsign"], a["latitude"], a["longitude"], a["altitude"], a["velocity"]) for a in aircraft_list]
    c.executemany("INSERT INTO aircraft_snapshots (callsign, latitude, longitude, altitude, velocity) VALUES (?,?,?,?,?)", data)
    conn.commit()
    conn.close()

def get_snapshots(limit=50):
    conn = connect()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, callsign, altitude, velocity, timestamp FROM aircraft_snapshots ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_distinct_timestamps():
    """Return list of unique snapshot timestamps for comparison dropdown"""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT DISTINCT timestamp FROM aircraft_snapshots ORDER BY timestamp DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_aircraft_by_timestamp(ts):
    """Return all aircraft from a given snapshot timestamp"""
    conn = connect()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT callsign FROM aircraft_snapshots WHERE timestamp = ?", (ts,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def compare_traffic(current_aircraft, previous_timestamp):
    """Compare current aircraft callsigns with a past snapshot"""
    current_callsigns = {a["callsign"] for a in current_aircraft if a["callsign"] != "N/A"}
    prev_aircraft = get_aircraft_by_timestamp(previous_timestamp)
    prev_callsigns = {a["callsign"] for a in prev_aircraft if a["callsign"] != "N/A"}
    return {
        "current_count": len(current_callsigns),
        "previous_count": len(prev_callsigns),
        "new": list(current_callsigns - prev_callsigns),
        "disappeared": list(prev_callsigns - current_callsigns),
        "common": len(current_callsigns & prev_callsigns),
        "previous_timestamp": previous_timestamp
    }