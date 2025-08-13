mport os
from dotenv import load_dotenv  # Required to load .env

# Load variables from .env file
load_dotenv()

# Fetch using the VARIABLE NAME, not the key value
API_KEY = os.getenv('SOLAR_API_KEY')  # Correct: 'SOLAR_API_KEY'
