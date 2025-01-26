import json
import time

import requests

import settings

headers = {"x-apikey": settings.api_key, "User-Agent": ""}


def get_or_save_data(url, file_name):
    requested = False
    try:
        with open(f"data/{file_name}", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        with open(f"data/{file_name}", "w") as f:
            r = requests.get(url, headers=headers)
            data = r.json()
            json.dump(data, f)
            requested = True
            print(f"Made a request {url}")

    return data, requested


def get_stations():
    url = "https://api1.raildata.org.uk/1033-stations-experience-apiv1_0/stations"
    file_name = "station_list.json"
    return get_or_save_data(url, file_name)


def get_station_accessibility_surveys(station_id):
    url = f"https://api1.raildata.org.uk/1033-stations-experience-apiv1_0/stations/{station_id}/accessibility/surveys"
    file_name = f"station_surveys_{station_id}.json"
    return get_or_save_data(url, file_name)


if __name__ == "__main__":

    stations, _ = get_stations()
    for station in stations["data"]["resultSet"]:
        print(station["name"], station["crsCode"])
        data, requested = get_station_accessibility_surveys(station["id"])
        if requested:
            time.sleep(0.5)
