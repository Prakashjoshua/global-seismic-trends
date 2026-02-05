import os
import requests
import pandas as pd
from datetime import datetime, timezone
os.makedirs("data", exist_ok=True)
records = []
for year in range(2020, 2025):
    for month in range(1, 13):
        start = f"{year}-{month:02d}-01"
        end = f"{year}-{month:02d}-28"
        print(f"Fetching data for {year}-{month:02d}")
        params = {
            "format": "geojson",
            "starttime": start,
            "endtime": end,
            "minmagnitude": 4
        }
        try:
            response = requests.get(
                "https://earthquake.usgs.gov/fdsnws/event/1/query",
                params=params,
                timeout=30
            )
            if response.status_code != 200:
                print(f"Failed for {year}-{month:02d}")
                continue
            data = response.json().get("features", [])
            for quake in data:
                prop = quake.get("properties", {})
                geo = quake.get("geometry", {})
                coords = geo.get("coordinates", [None, None, None])
                records.append({
                    "id": quake.get("id"),
                    "time": prop.get("time"),
                    "updated": prop.get("updated"),
                    "latitude": coords[1],
                    "longitude": coords[0],
                    "depth_km": coords[2],
                    "place": prop.get("place"),
                    "mag": prop.get("mag"),
                    "magType": prop.get("magType"),
                    "status": prop.get("status"),
                    "tsunami": prop.get("tsunami"),
                    "sig": prop.get("sig"),
                    "alert": prop.get("alert"),
                    "net": prop.get("net"),
                    "nst": prop.get("nst"),
                    "dmin": prop.get("dmin"),
                    "rms": prop.get("rms"),
                    "gap": prop.get("gap"),
                    "magError": prop.get("magError"),
                    "depthError": prop.get("depthError"),
                    "magNst": prop.get("magNst"),
                    "locationSource": prop.get("locationSource"),
                    "magSource": prop.get("magSource"),
                    "sources": prop.get("sources"),
                    "ids": prop.get("ids"),
                    "eventType": prop.get("type"),
                    "types": prop.get("types"),
                    "title": prop.get("title"),
                    "url": prop.get("url")
                })
        except Exception as e:
            print("Error:", e)
df = pd.DataFrame(records)
output_path = "raw_earthquake_data.csv"
try:
    if os.path.exists(output_path):
        os.remove(output_path)
except PermissionError:
    print("Permission Error, Fix It !")
    exit()
df.to_csv(output_path, index=False)
print("Completed Successfully.!")
print(f"File saved at: {output_path}")