import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import time
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh  # New autorefresh component

# Add this function
def get_real_solar_data(latitude, longitude, api_key):
    # Example for Solcast API
    url = f"https://api.solcast.com.au/radiation/forecasts?latitude={latitude}&longitude={longitude}&api_key={api_key}"
    response = requests.get(url)
    data = response.json()
    return data['forecasts'][0]['ghi']  # Global Horizontal Irradiance

# Then replace the current_solar_yield assignment with:
if data_source == "API Integration":
    current_solar_yield = get_real_solar_data(lat, lon, MmUM6JLgxgV5WVpYCrOqYLrkFJlBqaxR)

# Data setup
cities = ['Barcelona', 'Berlin', 'Cairo', 'Delhi', 'Dubai', 'London', 'Madrid', 'Melbourne',
          'Milan', 'Mumbai', 'Paris', 'Riyadh', 'Rome', 'Seville', 'Sydney']

# Realistic angle data for each surface type (in degrees)
surface_angles = {
    'hood': 15,    'roof': 5,     'rear_window': 45,  
    'rear_side_window': 30,  'front_side_window': 25,  'canopy': 0
}

# [YOUR SEGMENTS DATA HERE]

# Default values
default_utilization = 90
default_pv_efficiency = 25
default_cost = 350
default_transformation_efficiency = 90

# Streamlit app
st.set_page_config(layout="wide", page_title="VIPV Solar Tracker")
st.title("VIPV Solar Performance Tracker")
st.markdown("### Real-time Solar Yield Monitoring and Projections")

# Initialize session state for real-time data
if 'realtime_data' not in st.session_state:
    st.session_state.realtime_data = {
        'timestamps': [],
        'solar_yield': [],
        'power_output': [],
        'energy_generated': 0,
        'range_accumulated': 0,
        'savings_accumulated': 0
    }
    st.session_state.start_time = datetime.now(pytz.utc)

# Create tabs
tab1, tab2 = st.tabs(["Configuration", "Live Dashboard"])

with tab1:
    st.header("System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Region selection
        region = st.selectbox("Select Region", cities, index=cities.index('Dubai'))
        timezone = st.selectbox("Select Timezone", pytz.all_timezones, index=pytz.all_timezones.index('Europe/Madrid'))
        
    with col2:
        # Segment selection
        segment = st.selectbox("Select Vehicle", list(segments.keys()))
        segment_data = segments[segment]
        col2a, col2b = st.columns(2)
        with col2a:
            st.metric("WLTP Efficiency", f"{segment_data['wltp']} kWh/100km")
        with col2b:
            st.metric("City Efficiency", f"{segment_data['city']} kWh/100km")
    
    # Electricity price
    st.subheader("Energy Economics")
    col3, col4 = st.columns(2)
    with col3:
        electricity_price = st.slider("Electricity Price (€/kWh)",
                                      min_value=0.01, max_value=1.0,
                                      value=0.25, step=0.01)
    with col4:
        st.metric("Current Price", f"{electricity_price} €/kWh")

    st.subheader("PV Surface Configuration")
    surfaces_config = {}
    cols = st.columns(3)

    for i, (surface_name, surface_data) in enumerate(segment_data['surfaces'].items()):
        with cols[i % 3]:
            display_name = surface_name.replace('_', ' ').title()
            include = st.checkbox(f"Include {display_name}",
                                 value=surface_data.get('default', True),
                                 key=f"include_{surface_name}")

            if include:
                area = st.number_input(f"{display_name} Area (m²)",
                                      min_value=0.0,
                                      value=surface_data['area'],
                                      step=0.1,
                                      key=f"area_{surface_name}")

                utilization = st.slider(f"{display_name} Utilization (%)",
                                       min_value=0, max_value=100,
                                       value=default_utilization,
                                       key=f"util_{surface_name}")

                angle = st.slider(f"{display_name} Angle (°)",
                                 min_value=0, max_value=90,
                                 value=surface_data['angle'],
                                 key=f"angle_{surface_name}")

                efficiency = st.slider(f"{display_name} PV Efficiency (%)",
                                      min_value=0, max_value=100,
                                      value=default_pv_efficiency,
                                      key=f"eff_{surface_name}")

                surfaces_config[surface_name] = {
                    'area': area,
                    'utilization': utilization,
                    'angle': angle,
                    'efficiency': efficiency,
                    'include': True
                }
            else:
                surfaces_config[surface_name] = {'include': False}

    # Other parameters
    st.subheader("System Parameters")
    transformation_efficiency = st.slider("Energy Transformation Efficiency (%)",
                                         min_value=0, max_value=100,
                                         value=default_transformation_efficiency)
    
    # Real-time data source
    st.subheader("Data Source")
    data_source = st.radio("Select data source:", 
                          ["Simulated Data", "API Integration"], 
                          index=0)
    
    if data_source == "Simulated Data":
        st.session_state.simulated_yield = st.slider("Simulated Solar Yield (W/m²)", 
                 min_value=0, max_value=1500, 
                 value=800)
    else:
        st.info("API integration would be implemented here")

with tab2:
    st.header("Live Solar Performance Dashboard")
    
    # Initialize calculations
    total_area = 0
    total_efficiency = 0
    
    for surface_name, config in surfaces_config.items():
        if config.get('include', False):
            area = config['area'] * (config['utilization']/100)
            if 'side' in surface_name:
                area *= 2  # Both sides
            total_area += area
            total_efficiency = max(total_efficiency, config['efficiency'])  # Simplified
    
    # Dashboard layout
    col1, col2, col3, col4 = st.columns(4)
    
    # Get current solar yield
    if data_source == "Simulated Data":
        current_solar_yield = st.session_state.simulated_yield
    else:
        # For real API, you would fetch this value
        current_solar_yield = 850
    
    # Calculate current power output
    current_power = total_area * current_solar_yield * (total_efficiency/100) * (transformation_efficiency/100)
    
    # Calculate hourly energy (kWh)
    hourly_energy = current_power / 1000  # Convert W to kW
    
    # Update accumulated values
    now = datetime.now(pytz.utc)
    if st.session_state.realtime_data['timestamps']:
        last_time = st.session_state.realtime_data['timestamps'][-1]
        time_diff = (now - last_time).total_seconds() / 3600  # Hours
    else:
        time_diff = 0
    
    # Update accumulated values
    st.session_state.realtime_data['energy_generated'] += hourly_energy * time_diff
    st.session_state.realtime_data['range_accumulated'] += (hourly_energy * time_diff) / (segment_data['wltp'] / 100) * 100
    st.session_state.realtime_data['savings_accumulated'] += hourly_energy * time_diff * electricity_price
    
    # Add current data point
    st.session_state.realtime_data['timestamps'].append(now)
    st.session_state.realtime_data['solar_yield'].append(current_solar_yield)
    st.session_state.realtime_data['power_output'].append(current_power)
    
    # Keep only last 60 minutes of data
    if len(st.session_state.realtime_data['timestamps']) > 60:
        st.session_state.realtime_data['timestamps'] = st.session_state.realtime_data['timestamps'][-60:]
        st.session_state.realtime_data['solar_yield'] = st.session_state.realtime_data['solar_yield'][-60:]
        st.session_state.realtime_data['power_output'] = st.session_state.realtime_data['power_output'][-60:]
    
    # Display real-time metrics
    with col1:
        st.metric("Current Solar Yield", f"{current_solar_yield} W/m²")
    with col2:
        st.metric("Current Power Output", f"{current_power/1000:.2f} kW")
    with col3:
        st.metric("Hourly Energy", f"{hourly_energy:.3f} kWh")
    with col4:
        st.metric("Current Efficiency", f"{total_efficiency}%")
    
    st.markdown("---")
    
    col5, col6, col7 = st.columns(3)
    
    with col5:
        st.metric("Energy Generated", f"{st.session_state.realtime_data['energy_generated']:.2f} kWh")
    with col6:
        st.metric("Range Added", f"{st.session_state.realtime_data['range_accumulated']:.1f} km")
    with col7:
        st.metric("Savings Accumulated", f"{st.session_state.realtime_data['savings_accumulated']:.2f} €")
    
    st.markdown("---")
    
    # Create dataframe for real-time data
    realtime_df = pd.DataFrame({
        'Time': st.session_state.realtime_data['timestamps'],
        'Solar Yield (W/m²)': st.session_state.realtime_data['solar_yield'],
        'Power Output (W)': st.session_state.realtime_data['power_output']
    })
    
    # Create real-time charts
    if not realtime_df.empty:
        # Solar Yield Chart
        fig1 = px.line(realtime_df, x='Time', y='Solar Yield (W/m²)',
                      title='<b>Real-time Solar Yield</b>',
                      labels={'value': 'W/m²'},
                      template='plotly_dark')
        fig1.update_traces(line=dict(color='#FFA15A', width=3))
        fig1.update_layout(
            hovermode="x unified",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=12, color='white'),
            xaxis_title="Time",
            yaxis_title="Solar Yield (W/m²)",
            height=300
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Power Output Chart
        fig2 = px.line(realtime_df, x='Time', y='Power Output (W)',
                      title='<b>Real-time Power Output</b>',
                      labels={'value': 'Watts'},
                      template='plotly_dark')
        fig2.update_traces(line=dict(color='#19D3F3', width=3))
        fig2.update_layout(
            hovermode="x unified",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial", size=12, color='white'),
            xaxis_title="Time",
            yaxis_title="Power Output (W)",
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Projections
    st.subheader("Daily Projections")
    
    # Calculate projections based on current yield
    daylight_hours = 10  # Average daylight hours
    projected_energy = st.session_state.realtime_data['energy_generated'] + (hourly_energy * daylight_hours)
    projected_range = st.session_state.realtime_data['range_accumulated'] + ((hourly_energy * daylight_hours) / (segment_data['wltp'] / 100) * 100)
    projected_savings = st.session_state.realtime_data['savings_accumulated'] + (hourly_energy * daylight_hours * electricity_price)
    
    col8, col9, col10 = st.columns(3)
    
    with col8:
        st.metric("Projected Daily Energy", f"{projected_energy:.2f} kWh", 
                 delta=f"+{projected_energy - st.session_state.realtime_data['energy_generated']:.2f} kWh")
    with col9:
        st.metric("Projected Daily Range", f"{projected_range:.1f} km", 
                 delta=f"+{projected_range - st.session_state.realtime_data['range_accumulated']:.1f} km")
    with col10:
        st.metric("Projected Daily Savings", f"{projected_savings:.2f} €", 
                 delta=f"+{projected_savings - st.session_state.realtime_data['savings_accumulated']:.2f} €")
    
    # Add refresh button
    if st.button("Refresh Data", type="primary"):
        st.experimental_rerun()
    
    # Add auto-refresh component
    st.markdown("---")
    refresh_rate = st.slider("Auto-refresh rate (seconds)", 5, 60, 10)
    auto_refresh = st_autorefresh(interval=refresh_rate * 1000, key="data_refresh")

# Footer
st.markdown("---")
st.markdown("VIPV Solar Tracker • Real-time Monitoring System")
st.markdown("Data updates automatically • Configuration can be adjusted in the Configuration tab")
