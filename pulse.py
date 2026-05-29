"""Python script that:
- Takes a URL as input
- Sends an HTTP GET request to the URL
- Calculate how long it took the server to respond (in milliseconds)
- Print a clean message to the terminal with the URL, HTTP Status Code, and Response time.
"""
import requests
import time
import sqlite3
from datetime import datetime, timezone


url = input("Enter url: ")
db_name = 'metrics.db'
# Initialize database
conn = sqlite3.connect(db_name)
cursor = conn.cursor()
# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        url TEXT,
        status_code INTEGER,
        time_ms REAL,
        error TEXT
    )
''')
conn.commit()

def ping_url(url):
    """Function that pings a website.
    Args:
        url (string): website url
    Returns:
        A dictionary containing timestamp, url, status code, time (in ms), and error
    """
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        r = requests.get(url, timeout=5)
        duration_ms = r.elapsed.total_seconds() * 1000
    except requests.exceptions.ReadTimeout as errrt:
        return {"timestamp": current_time, "url": url, "status_code": None, "time_ms": None, "error": "Time out"}
    except requests.exceptions.MissingSchema as errmiss:
        return {"timestamp": current_time, "url": url, "status_code": None, "time_ms": None, "error": "Missing schema: check URL and try again"}
    except requests.exceptions.ConnectionError as conerr:
        return {"timestamp": current_time, "url": url, "status_code": None, "time_ms": None, "error": "Connection error"}
    
    return {"timestamp": current_time, "url": url, "status_code": r.status_code, "time_ms": duration_ms, "error": None}


print(f"Monitoring {url}... Press Ctrl+C to stop.")

try:
    while True:
        # Get data
        data = ping_url(url)
        
        # Insert into SQLite
        query = '''INSERT INTO pings (timestamp, url, status_code, time_ms, error)
                    VALUES (:timestamp, :url, :status_code, :time_ms, :error)'''
        cursor.execute(query, data)
        conn.commit()
        # Print output on terminal
        time_str = f"{data['time_ms']:.2f}ms" if data['time_ms'] else "N/A"
        print(f"{data['timestamp']} - {data['status_code']} - {time_str}")
        time.sleep(5)  # 5secs pause
except KeyboardInterrupt:
    print("\nMonitoring stopped.")
finally:
    # Close connection
    conn.close()
