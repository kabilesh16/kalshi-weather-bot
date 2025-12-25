import requests

station_id = "KNYC"  # Central Park, NYC
url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
url2 = "https://api.open-meteo.com/v1/forecast?latitude=40.78&longitude=-73.96&hourly=temperature_2m,precipitation"

response2 = requests.get(url2)
data2 = response2.json()
response = requests.get(url)
data = response.json()

temp_c = data['properties']['temperature']['value']
precip_mm = data['properties']['precipitationLastHour']['value']

print(f"Temperature: {temp_c} °C")
print(f"Precipitation last hour: {precip_mm} mm")

def get_current_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "current_weather" not in data:
        return "No weather data found."

    weather = data["current_weather"]

    return {
        "temperature_c": weather["temperature"]
    }

# Los Angeles
lat = 34.05
lon = -118.24

weather = get_current_weather(lat, lon)
print(weather)
