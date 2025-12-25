import requests
import pandas as pd

def load_nyc_daily_highs(
    start_date="1995-01-01",
    end_date="2024-12-31"
):
    """
    Loads historical daily high temperatures for NYC (Central Park)
    using Open-Meteo Archive API.
    """

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": 40.78,
        "longitude": -73.96,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m",
        "timezone": "America/New_York"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame({
        "time": pd.to_datetime(data["hourly"]["time"]),
        "temperature": data["hourly"]["temperature_2m"]
    })

    df["date"] = df["time"].dt.date

    daily_highs = (
        df.groupby("date")["temperature"]
        .max()
        .reset_index(name="high_temp")
    )

    daily_highs["date"] = pd.to_datetime(daily_highs["date"])
    return daily_highs
