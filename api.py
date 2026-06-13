from fastapi import FastAPI
import sqlite3
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all frontends to connect
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Sentinel API is running"}

@app.get("/status")
def status():
    """Get the most recent result for each URL."""
    conn = sqlite3.connect("metrics.db")
    conn.row_factory = sqlite3.Row  # Makes database rows act like dictionaries
    try:
        cursor = conn.cursor()
        query = """SELECT url, status_code, time_ms, error, MAX(timestamp) 
                    AS last_checked FROM pings GROUP BY url"""
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert rows to a list of real dictionaries
        list_of_dicts = [dict(row) for row in rows]
    finally:
        conn.close()
        
    return list_of_dicts #json_data

@app.get("/history")
def history(url: str):
    """Query the database for the last 10 pings."""
    conn = sqlite3.connect('metrics.db')
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        query = """SELECT * FROM pings WHERE url = ?
                    ORDER BY timestamp DESC
                    LIMIT 10"""
        cursor.execute(query, (url,))
        rows = cursor.fetchall()
        list_of_dicts = [dict(row) for row in rows]
    finally:
        conn.close()
    
    return list_of_dicts