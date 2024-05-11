import requests
import json

data = requests.get("https://api.openalex.org/works/W1009208869").json()

print(data["authorships"])
