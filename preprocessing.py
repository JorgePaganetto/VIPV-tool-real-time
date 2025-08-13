# preprocessing.py
from api_service import fetch_solar_data

def preprocess_inputs(location, date):
    weather = fetch_solar_data(location, date)
    return clean_data(weather)  # Add to your dataset
