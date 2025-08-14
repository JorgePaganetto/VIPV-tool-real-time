import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_solar_data(lat, lon):
    API_KEY = os.getenv('SOLAR_API_KEY')  # CORRECT - use variable name
    API_URL = "https://api.actual-provider.com/endpoint"  # REPLACE with real API URL
    
    params = {
        'lat': lat,
        'lon': lon,
        'api_key': API_KEY,
        'units': 'metric'
    }
    
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None
