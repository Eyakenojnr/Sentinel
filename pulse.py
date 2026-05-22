"""Python script that:
- Takes a URL as input
- Sends an HTTP GET request to the URL
- Calculate how long it took the server to respond (in milliseconds)
- Print a clean message to the terminal with the URL, HTTP Status Code, and Response time.
"""
import requests
import time

url = input("Enter url: ")

try:
    r = requests.get(url, timeout=1, verify=True)
    duration_ms = r.elapsed.total_seconds() * 1000
    print(f'The url {url} with status code [{r.status_code}] took {duration_ms}ms to respond.')
except requests.exceptions.ReadTimeout as errrt:
    print("Time out")
except requests.exceptions.MissingSchema as errmiss:
    print("Missing schema: check the url and try again.")
except requests.exceptions.ConnectionError as conerr:
    print("Connection error")
