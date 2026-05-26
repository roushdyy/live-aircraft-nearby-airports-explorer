import sqlite3
from typing import List, Dict, Optional, Any

DB_NAME = "aircraft.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

# ========== SEARCH HISTORY ==========
def save_search(city: str, lat: float, lon: float) -> int:
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO searches (city, latitude, longitude, search_time) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (city, lat, lon))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def get_search_history(limit: int = 20) -> List[dict]:
    conn = connect_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, city, latitude, longitude, search_time FROM searches ORDER BY search_time DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_search(search_id: int) -> bool:
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM searches WHERE id = ?", (search_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted

# ========== AIRCRAFT SNAPSHOTS ==========
def save_multiple_aircraft_snapshots(aircraft_list: List[dict]) -> int:
    if not aircraft_list:
        return 0
    conn = connect_db()
    cur = conn.cursor()
    data = [(a.get("callsign", "N/A"), a.get("latitude"), a.get("longitude"), a.get("altitude"), a.get("velocity")) for a in aircraft_list]
    cur.executemany("INSERT INTO aircraft_snapshots (callsign, latitude, longitude, altitude, velocity, timestamp) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)", data)
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count

def get_aircraft_snapshots(limit: int = 100) -> List[dict]:
    conn = connect_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, callsign, latitude, longitude, altitude, velocity, timestamp FROM aircraft_snapshots ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ========== BOOKMARKED AIRPORTS ==========
def save_bookmarked_airport(airport_name: str, icao: str) -> int:
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM saved_airports WHERE icao = ?", (icao,))
    if cur.fetchone():
        conn.close()
        return -1
    cur.execute("INSERT INTO saved_airports (airport_name, icao, saved_time) VALUES (?, ?, CURRENT_TIMESTAMP)", (airport_name, icao))
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

def get_bookmarked_airports() -> List[dict]:
    conn = connect_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, airport_name, icao, saved_time FROM saved_airports ORDER BY saved_time DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_bookmarked_airport(airport_id: int) -> bool:
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM saved_airports WHERE id = ?", (airport_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted

# ========== COMPARE TRAFFIC ==========
def compare_traffic(current_aircraft_list: List[dict]) -> dict:
    result = {"current_count": len(current_aircraft_list), "previous_count": 0, "new_aircraft": [], "disappeared_aircraft": [], "common_count": 0, "timestamp_previous": None}
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT timestamp FROM aircraft_snapshots ORDER BY timestamp DESC LIMIT 1")
    row = cur.fetchone()
    if row:
        result["timestamp_previous"] = row[0]
        cur.execute("SELECT DISTINCT callsign FROM aircraft_snapshots WHERE timestamp = ?", (row[0],))
        prev_callsigns = {r[0] for r in cur.fetchall()}
        result["previous_count"] = len(prev_callsigns)
        curr_callsigns = {a.get("callsign") for a in current_aircraft_list if a.get("callsign")}
        result["new_aircraft"] = list(curr_callsigns - prev_callsigns)
        result["disappeared_aircraft"] = list(prev_callsigns - curr_callsigns)
        result["common_count"] = len(curr_callsigns & prev_callsigns)
    conn.close()
    return result

def get_snapshot_list(limit: int = 20) -> List[dict]:
    conn = connect_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT timestamp, COUNT(*) as aircraft_count FROM aircraft_snapshots GROUP BY timestamp ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]