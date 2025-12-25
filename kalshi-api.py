import requests

markets_url = "https://api.elections.kalshi.com/trade-api/v2/markets"
params = {
    "series_ticker": "KXHIGHNY",
    "status": "open"
}

markets_response = requests.get(markets_url, params=params)
markets_data = markets_response.json()

print("\nActive markets in KXHIGHNY series:")
for market in markets_data["markets"]:
    print(f"- {market['ticker']}: {market['title']}")
    print(f"  Event: {market['event_ticker']}")
    print(f"  Yes Price: {market['yes_bid']}¢ | Volume: {market['volume']}")
    print()

if markets_data["markets"]:
    first_market = markets_data["markets"][0]
    event_ticker = first_market["event_ticker"]

    event_url = f"https://api.elections.kalshi.com/trade-api/v2/events/{event_ticker}"
    event_response = requests.get(event_url)
    event_data = event_response.json()

    print("Event Details:")
    print(f"Title: {event_data['event']['title']}")
    print(f"Category: {event_data['event']['category']}")
