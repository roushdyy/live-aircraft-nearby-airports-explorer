
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