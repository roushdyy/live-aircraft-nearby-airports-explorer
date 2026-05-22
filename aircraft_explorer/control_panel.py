
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any

DB_NAME = "aircraft.db"

def connect_db():
    """Return a database connection."""
    return sqlite3.connect(DB_NAME)
# save history of user
def save_search(city: str, latitude: float, longitude: float) -> int:
    """
    Save a user search into the 'searches' table.
    Returns the ID of the inserted record.
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO searches (city, latitude, longitude, search_time)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (city, latitude, longitude))
    conn.commit()
    search_id = cursor.lastrowid
    conn.close()
    return search_id
def get_search_history(limit: int = 20) -> List[Dict[str, Any]]:
    """Retrieve the most recent searches (limit)."""
    conn = connect_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, city, latitude, longitude, search_time
        FROM searches
        ORDER BY search_time DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
def delete_search(search_id: int) -> bool:
    """Delete a specific search record by its ID. Returns True if deleted."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM searches WHERE id = ?", (search_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
def delete_all_searches() -> int:
    """Delete all search history. Returns number of deleted rows."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM searches")
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count
#==================== AIRCRAFT SNAPSHOTS ====================

def save_aircraft_snapshot(callsign: str, latitude: float, longitude: float,
                           altitude: Optional[float], velocity: Optional[float]) -> int:
    """
    Save one aircraft's current state into aircraft_snapshots.
    Returns snapshot ID.
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO aircraft_snapshots (callsign, latitude, longitude, altitude, velocity, timestamp)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (callsign, latitude, longitude, altitude, velocity))
    conn.commit()
    snap_id = cursor.lastrowid
    conn.close()
    return snap_id


def save_multiple_aircraft_snapshots(aircraft_list: List[Dict]) -> int:
    """
    Bulk insert many aircraft snapshots.
    aircraft_list: list of dicts with keys: callsign, latitude, longitude, altitude, velocity
    Returns number of inserted records.
    """
    if not aircraft_list:
        return 0
    conn = connect_db()
    cursor = conn.cursor()
    data = []
    for a in aircraft_list:
        data.append((
            a.get("callsign", "N/A"),
            a.get("latitude"),
            a.get("longitude"),
            a.get("altitude"),
            a.get("velocity")
        ))
    cursor.executemany("""
        INSERT INTO aircraft_snapshots (callsign, latitude, longitude, altitude, velocity, timestamp)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, data)
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count


def get_aircraft_snapshots(limit: int = 100, after_timestamp: Optional[str] = None) -> List[Dict]:
    """
    Retrieve aircraft snapshots, optionally filtered by timestamp.
    Returns list of dicts sorted by timestamp desc.
    """
    conn = connect_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if after_timestamp:
        cursor.execute("""
            SELECT id, callsign, latitude, longitude, altitude, velocity, timestamp
            FROM aircraft_snapshots
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (after_timestamp, limit))
    else:
        cursor.execute("""
            SELECT id, callsign, latitude, longitude, altitude, velocity, timestamp
            FROM aircraft_snapshots
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_latest_snapshot_timestamp() -> Optional[str]:
    """Return the timestamp of the most recent snapshot (for comparison)."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(timestamp) FROM aircraft_snapshots")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else None


# ==================== BOOKMARKED AIRPORTS ====================

def save_bookmarked_airport(airport_name: str, icao: str) -> int:
    """Add an airport to saved_airports. Returns ID."""
    conn = connect_db()
    cursor = conn.cursor()
    # Avoid duplicates by ICAO
    cursor.execute("SELECT id FROM saved_airports WHERE icao = ?", (icao,))
    if cursor.fetchone():
        conn.close()
        return -1  # Already saved
    cursor.execute("""
        INSERT INTO saved_airports (airport_name, icao, saved_time)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (airport_name, icao))
    conn.commit()
    saved_id = cursor.lastrowid
    conn.close()
    return saved_id


def get_bookmarked_airports() -> List[Dict]:
    """Retrieve all bookmarked airports."""
    conn = connect_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, airport_name, icao, saved_time
        FROM saved_airports
        ORDER BY saved_time DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_bookmarked_airport(airport_id: int) -> bool:
    """Delete a bookmarked airport by its ID."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_airports WHERE id = ?", (airport_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def delete_bookmarked_airport_by_icao(icao: str) -> bool:
    """Delete by ICAO code."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_airports WHERE icao = ?", (icao,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# ==================== COMPARE TRAFFIC ====================

def compare_traffic(current_aircraft_list: List[Dict],
                    previous_snapshot_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Compare the current aircraft list with a previous snapshot.
    If no previous_snapshot_id given, use the most recent snapshot.
    Returns a dict with:
        - current_count
        - previous_count
        - new_aircraft (list of callsigns only in current)
        - disappeared_aircraft (list only in previous)
        - common_count
        - timestamp_previous
    """
    result = {
        "current_count": len(current_aircraft_list),
        "previous_count": 0,
        "new_aircraft": [],
        "disappeared_aircraft": [],
        "common_count": 0,
        "timestamp_previous": None
    }

    conn = connect_db()
    cursor = conn.cursor()

    # If no previous snapshot ID given, get the most recent one
    if previous_snapshot_id is None:
        cursor.execute("SELECT id, timestamp FROM aircraft_snapshots ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            previous_snapshot_id = row[0]
            result["timestamp_previous"] = row[1]
        else:
            conn.close()
            return result  # No previous data
    else:
        cursor.execute("SELECT timestamp FROM aircraft_snapshots WHERE id = ?", (previous_snapshot_id,))
        row = cursor.fetchone()
        if row:
            result["timestamp_previous"] = row[0]

    # Get previous aircraft callsigns for that snapshot (limit to same timestamp range)
    # Note: aircraft_snapshots stores individual records; we assume one snapshot = many records with same timestamp.
    # We'll get the distinct callsigns from the closest timestamp to that snapshot's time.
    # Simpler: use the timestamp of that snapshot to fetch all records with that exact timestamp.
    if result["timestamp_previous"]:
        cursor.execute("""
            SELECT DISTINCT callsign FROM aircraft_snapshots
            WHERE timestamp = ?
        """, (result["timestamp_previous"],))
        previous_callsigns = {row[0] for row in cursor.fetchall()}
        result["previous_count"] = len(previous_callsigns)

        current_callsigns = {a.get("callsign") for a in current_aircraft_list if a.get("callsign")}
        result["new_aircraft"] = list(current_callsigns - previous_callsigns)
        result["disappeared_aircraft"] = list(previous_callsigns - current_callsigns)
        result["common_count"] = len(current_callsigns & previous_callsigns)

    conn.close()
    return result


def get_snapshot_list(limit: int = 20) -> List[Dict]:
    """
    Return list of previous snapshots with their timestamps and aircraft counts.
    Useful for UI dropdowns.
    """
    conn = connect_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, COUNT(*) as aircraft_count
        FROM aircraft_snapshots
        GROUP BY timestamp
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ==================== CLEANUP & HELPERS ====================

def delete_old_snapshots(days: int = 7) -> int:
    """Delete snapshots older than 'days' days. Returns number deleted."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM aircraft_snapshots
        WHERE timestamp < datetime('now', '-' || ? || ' days')
    """, (days,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count