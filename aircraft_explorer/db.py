import sqlite3

DB_NAME = "aircraft.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    # User searches
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Airports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS airports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        airport_name TEXT,
        icao TEXT,
        iata TEXT,
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
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Bookmarked airports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_airports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        airport_name TEXT,
        icao TEXT,
        saved_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

    print("Database tables created.")

# Run directly
if __name__ == "__main__":
    create_tables()