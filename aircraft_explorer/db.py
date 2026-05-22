import sqlite3

DATABASE = "aircraft.db"


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
        latitude REAL,
        longitude REAL
    )
    """)

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
def load_airports_from_csv(csv_path="data/airports.csv"):
    import csv
    conn = connect_db()
    cursor = conn.cursor()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row['latitude_deg'])
                lon = float(row['longitude_deg'])
                if lat == 0 and lon == 0:
                    continue
                cursor.execute("""
                    INSERT OR IGNORE INTO airports (airport_name, icao, iata, latitude, longitude)
                    VALUES (?, ?, ?, ?, ?)
                """, (row['name'], row['ident'], row.get('iata_code', ''), lat, lon))
            except:
                continue
    conn.commit()
    conn.close()