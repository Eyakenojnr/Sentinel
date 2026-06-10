from fastapi import FastAPI
import sqlite3


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Sentinel API is running"}

@app.get("/status")
def status():
    conn = sqlite3.connect("metrics.db")
    conn.row_factory = sqlite3.Row
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