import requests

url = "https://opensky-network.org/api/states/all"

response = requests.get(url)

data = response.json()