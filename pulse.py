"""Python script that:
- Takes a URL as input
- Sends an HTTP GET request to the URL
- Calculate how long it took the server to respond (in milliseconds)
- Print a clean message to the terminal with the URL, HTTP Status Code, and Response time.
"""
import requests
import time
import csv
import os
from datetime import datetime, timezone

url = input("Enter url: ")
output_file = 'metrics.csv'

def ping_url(url):
    """Function that pings a website.
    Args:
        url (string): website url
    Returns:
        A dictionary containing timestamp, url, status code, time (in ms), and error
    """
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        r = requests.get(url, timeout=5, verify=True)
        duration_ms = r.elapsed.total_seconds() * 1000
    except requests.exceptions.ReadTimeout as errrt:
        return {"timestamp": current_time, "url": url, "status_code": None, "time_ms": None, "error": "Time out"}
    except requests.exceptions.MissingSchema as errmiss:
        return {"timestamp": current_time, "url": url, "status_code": None, "time_ms": None, "error": "Missing schema: check URL and try again"}
    except requests.exceptions.ConnectionError as conerr:
        return {"timestamp": current_time, "url": url, "status_code": None, "time_ms": None, "error": "Connection error"}
    
    return {"timestamp": current_time, "url": url, "status_code": r.status_code, "time_ms": duration_ms, "error": None}


# Check if file exists before writing to it, this prevent writing  CSV header multiple times when appending to the file
file_exists = os.path.isfile(output_file)
needs_header = not file_exists or os.path.getsize(output_file) == 0  # Header is only needed if file doesn't exist OR if it is empty (0 bytes)

with open(output_file, 'a', newline='') as csvfile:
    field_names = ['timestamp', 'url', 'status_code', 'time_ms', 'error']
    writer = csv.DictWriter(csvfile, fieldnames=field_names)
    
    if needs_header:
        writer.writeheader()
        csvfile.flush()  # Ensures header is written immediately
    
    print(f"Monitoring {url}... Press Ctrl+C to stop.")
    
    try:
        while True:
            result = ping_url(url)
            writer.writerow(result)
            csvfile.flush()  # Force Python to write to file immediately to prevent data loss
            # Check if data exists before printing to console
            time_str = f"{result['time_ms']:.2f}ms" if result['time_ms'] else "N/A"
            print(f"{result['timestamp']} - {result['status_code']} - {time_str}")
            time.sleep(5)  # Pause for 5 secs
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
