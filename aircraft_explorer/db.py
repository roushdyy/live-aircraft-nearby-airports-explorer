import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), "aircraft.db")


def connect_db():
    return sqlite3.connect(DATABASE)


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Search history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        latitude REAL,
        longitude REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Saved airports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_airports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        airport_name TEXT,
        icao TEXT,
        latitude REAL,
        longitude REAL,
        saved_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Ensure older DBs gain the saved_time column if it was added later
    cursor.execute("PRAGMA table_info(saved_airports)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'saved_time' not in columns:
        cursor.execute("ALTER TABLE saved_airports ADD COLUMN saved_time DATETIME DEFAULT CURRENT_TIMESTAMP")

    # Aircraft snapshots
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aircraft_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        callsign TEXT,
        latitude REAL,
        longitude REAL,
        altitude REAL,
        velocity REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_search(city, lat, lon):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO searches (city, latitude, longitude)
    VALUES (?, ?, ?)
    """, (city, lat, lon))

    conn.commit()
    conn.close()


def get_searches():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM searches ORDER BY timestamp DESC")

    results = cursor.fetchall()

    conn.close()

    return results
