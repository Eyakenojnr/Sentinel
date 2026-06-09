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


URLS = [
    "https://google.com",
    "https://httpstat.us/500",
    "http://this-is-a-bad-url.com",
    "https://github.com"
]
INTERVAL = 5
DB_NAME = "metrics.db"


class Database:
    def __init__(self, db_name):
        """Connects to SQLite and creates a table."""
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                url TEXT,
                status_code INTEGER,
                time_ms REAL,
                error TEXT
            )
        """)
        self.conn.commit()
        
    def insert_pings(self, ping_results):
        """Batch inserts a list of dictionaries."""
        query = """INSERT INTO pings (timestamp, url, status_code, time_ms, error)
                    VALUES (:timestamp, :url, :status_code, :time_ms, :error)"""
        self.cursor.executemany(query, ping_results)
        self.conn.commit()
        
    def close(self):
        self.conn.close()
        
        
class SentinelMonitor:
    def __init__(self, urls, db_name):
        """Instantiate Database class and ThreadPoolExecutor."""
        self.db = Database(db_name)
        self.urls = urls
                
                
    def _ping_url(self, url):
        """Private method to ping a single URL."""
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            r = requests.get(url, timeout=4)
            return {
                "timestamp": current_time, "url": url,
                "status_code": r.status_code,
                "time_ms": r.elapsed.total_seconds() * 1000,
                "error": None
            }
        except requests.exceptions.ReadTimeout as errt:
            return {"timestamp": current_time, "url": url, "status_code": None, "time_ms": None, "error": "Time out"}
        except requests.exceptions.MissingSchema as errmiss:
            return {"timestamp": current_time, "url": url, "status_code": None, "time_ms": None, "error": "Missing Schema: check URL and try again"}
        except requests.exceptions.ConnectionError as conerr:
            return {"timestamp": current_time, "url": url, "status_code": None, "time_ms": None, "error": "Connection error"}
    
    
    
    def run(self):
        print(f"Sentinel active. Monitoring {len(self.urls)} targets...")
        
        with ThreadPoolExecutor(max_workers=len(self.urls)) as executor:
            try:
                while True:
                    start_tick = time.perf_counter()  # Record precise starting time
                    batch_results = []
                    
                    # Start concurrent pings
                    future_to_url = {executor.submit(self._ping_url, url): url for url in self.urls}

                    # Collect results as they finnish
                    for future in as_completed(future_to_url):
                        result = future.result()  # Converts future object to a dictionary
                        batch_results.append(result)
                        
                        # Live feedback to terminal
                        status = result['status_code'] or "ERR"
                        print(f"[{result['timestamp']}] {result['url']}: {status}")
                    
                    # Batch insert everything at once
                    self.db.insert_pings(batch_results)
                    
                    # Handle time drift
                    elapsed = time.perf_counter() - start_tick
                    sleep_time = max(0, INTERVAL - elapsed)
                    time.sleep(sleep_time)
            except KeyboardInterrupt:
                print(f"\nMonitoring stopped by user.")
            finally:
                self.db.close()
                

if __name__ == "__main__":
    monitor = SentinelMonitor(URLS, DB_NAME)
    monitor.run()
