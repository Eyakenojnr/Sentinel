"""Python script that:
- Takes a URL as input
- Sends an HTTP GET request to the URL
- Calculate how long it took the server to respond (in milliseconds)
- Print a clean message to the terminal with the URL, HTTP Status Code, and Response time.
"""
import requests
import time

url = input("Enter url: ")

def ping_url(url):
    """Function that pings a website.
    Args:
        url (string): website url
    Returns:
    A dictionary
    """
    try:
        r = requests.get(url, timeout=1, verify=True)
        duration_ms = r.elapsed.total_seconds() * 1000
    except requests.exceptions.ReadTimeout as errrt:
        print("Time out")
        return {"url": url, "status_code": None, "time_ms": None, "error": "Time out"}
    except requests.exceptions.MissingSchema as errmiss:
        print("Missing schema: check the url and try again.")
        return {"url": url, "status_code": None, "time_ms": None, "error": "Missing schema"}
    except requests.exceptions.ConnectionError as conerr:
        print("Connection error")
        return {"url": url, "status_code": None, "time_ms": None, "error": "Connection error"}
    
    return {"url": url, "status_code": r.status_code, "time_ms": duration_ms, "error": None}


while True:
    print(ping_url(url))
    time.sleep(5)  # Pause for 5 secs
