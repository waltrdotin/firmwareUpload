import requests

response = requests.get("https://api.waltr.in/v0/ping")
print(response.status_code)
print(response.json())



