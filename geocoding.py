import pandas as pd
import requests
import time

df = pd.read_csv("raw_places.csv")

def geocode(place, city, country):
    query = f"{place}, {city}, {country}"
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json"
    response = requests.get(url, headers={"User-Agent": "geo-script"})
    data = response.json()
    if data:
        return data[0]["lat"], data[0]["lon"]
    return None, None

latitudes = []
longitudes = []

for _, row in df.iterrows():
    lat, lon = geocode(row["place_name"], row.get("city", ""), row["country"])
    latitudes.append(lat)
    longitudes.append(lon)
    time.sleep(1)  # To respect Nominatim's rate limit

df["latitude"] = latitudes
df["longitude"] = longitudes
df.to_csv("places_with_coordinates.csv", index=False)
