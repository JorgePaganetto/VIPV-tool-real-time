import requests

def fetch_solar_data(latitude, longitude, date):
    API_URL = "https://api.example.com/solar"
    params = {
        'lat': latitude,
        'lon': longitude,
        'date': date,
        'api_key': 'YOUR_API_KEY'
    }
    response = requests.get(API_URL, params=params)
    response.raise_for_status()  # Raise errors for HTTP failures
    return response.json()
