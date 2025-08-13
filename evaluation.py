from api_service import fetch_solar_data

def evaluate_car_performance(location, date):
    # Fetch solar data from API
    solar_data = fetch_solar_data(location['lat'], location['lon'], date)
    
    # Use API data in calculations (e.g., energy prediction)
    energy_generated = solar_data['irradiance'] * panel_area * efficiency
    return energy_generated
