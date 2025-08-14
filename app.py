import streamlit as st
from api_service import fetch_solar_data

st.title("PV Panel Car Evaluation")

# User inputs
lat = st.number_input("Latitude", value=40.7128)
lon = st.number_input("Longitude", value=-74.0060)

if st.button("Calculate Solar Potential"):
    with st.spinner("Fetching solar data..."):
        solar_data = fetch_solar_data(lat, lon)
        
    if solar_data:
        st.success("Data retrieved successfully!")
        st.write("Solar Irradiance:", solar_data['irradiance'])
        # Add your PV car calculations here
    else:
        st.error("Failed to retrieve solar data")
