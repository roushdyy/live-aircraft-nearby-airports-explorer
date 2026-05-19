import sqlite3

DB_NAME = "aircraft.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    # User searches
    cursor.execute()

    # Airports
    cursor.execute()

    # Aircraft snapshots
    cursor.execute()

    # Bookmarked airports
    
    cursor.execute()

    conn.commit()
    conn.close()

    print("Database tables created.")

# Recreate tables if they don't exist
if __name__ == "__main__":
    create_tables()