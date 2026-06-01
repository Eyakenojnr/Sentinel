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
from concurrent.futures import ThreadPoolExecutor, as_completed


urls = [
    "https://google.com",
    "https://httpstat.us/500",
    "http://this-is-a-bad-url.com",
    "https://github.com"
] #input("Enter url: ")
db_name = 'metrics.db'
# Initialize database
conn = sqlite3.connect(db_name, check_same_thread=False)
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


print(f"Monitoring {urls}... Press Ctrl+C to stop.")

try:
    while True:
        start_loop = time.time()
        
        # Using ThreadPoolExecutor to ping all URLs at once
        with ThreadPoolExecutor(max_workers=len(urls)) as executor:
            # Map the function to the URLs
            future_to_url = {executor.submit(ping_url, url): url for url in urls}
            
            # Process results as they finish
            for future in as_completed(future_to_url):
                data = future.result()
                # Insert into SQLite    
                query = '''INSERT INTO pings (timestamp, url, status_code, time_ms, error)
                            VALUES (:timestamp, :url, :status_code, :time_ms, :error)'''
                cursor.execute(query, data)
                conn.commit()
                # Print output on terminal
                time_str = f"{data['time_ms']:.2f}ms" if data['time_ms'] else "N/A"
                print(f"[{data['timestamp']}] {data['url']} -> {data['status_code']} ({time_str})")
                
            # 5secs pause
            time.sleep(5)
except KeyboardInterrupt:
    print("\nMonitoring stopped.")
finally:
    conn.close()
