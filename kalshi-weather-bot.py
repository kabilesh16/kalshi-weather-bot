import requests

station_id = "KNYC"  # Central Park, NYC
url = f"https://api.weather.gov/stations/{station_id}/observations/latest"

response = requests.get(url)
data = response.json()

temp_c = data['properties']['temperature']['value']  # in Celsius
precip_mm = data['properties']['precipitationLastHour']['value']

print(f"Temperature: {temp_c} °C")
print(f"Precipitation last hour: {precip_mm} mm")
