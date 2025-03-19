import streamlit as st
import ee
import geemap
import plotly.express as px
from datetime import datetime, timedelta
import folium
from data_processor import CarbonSequestrationProcessor
import os

# Initialize Earth Engine with better error handling
def initialize_earth_engine():
    try:
        ee.Initialize()
    except Exception as e:
        st.error("""
        ### Earth Engine Authentication Required
        
        To use this dashboard, you need to:
        
        1. Sign up for Google Earth Engine at https://earthengine.google.com/
        2. Register your project at https://console.cloud.google.com/
        3. Enable the Earth Engine API
        4. Create service account credentials
        
        After completing these steps, run:
        ```bash
        earthengine authenticate --force
        ```
        
        Error details: {}
        """.format(str(e)))
        st.stop()

# Initialize Earth Engine
initialize_earth_engine()

# Page config
st.set_page_config(
    page_title="Carbon Sequestration Dashboard",
    page_icon="🌳",
    layout="wide"
)

# Title and description
st.title("🌳 Carbon Sequestration Dashboard")
st.markdown("""
This dashboard estimates and visualizes carbon sequestration in the Berkshire Taconic Landscape 
using satellite imagery and AI-powered analysis.
""")

# Initialize the processor
@st.cache_resource
def init_processor():
    return CarbonSequestrationProcessor()

# Define the region of interest (Berkshire Taconic Landscape)
roi = ee.Geometry.Rectangle([-73.5, 42.0, -73.0, 42.5])

# Sidebar controls
st.sidebar.header("Controls")
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(
        datetime.now() - timedelta(days=365),
        datetime.now()
    ),
    max_value=datetime.now()
)

# Initialize the processor
try:
    processor = init_processor()
except Exception as e:
    st.error(f"Error initializing Earth Engine: {str(e)}")
    st.info("Please follow the authentication steps above.")
    st.stop()

# Main content
col1, col2 = st.columns(2)

with col1:
    st.subheader("Carbon Storage Map")
    
    # Get the latest carbon storage data
    end_date = date_range[1].strftime('%Y-%m-%d')
    start_date = date_range[0].strftime('%Y-%m-%d')
    
    try:
        # Get NDVI time series
        ndvi_series = processor.get_ndvi_time_series(roi, start_date, end_date)
        mean_ndvi = ndvi_series.mean()
        
        # Calculate carbon storage
        carbon_storage = processor.estimate_carbon_storage(mean_ndvi)
        
        # Create the map
        Map = geemap.Map(center=[42.25, -73.25], zoom=10)
        Map.addLayer(carbon_storage, {'min': 0, 'max': 200, 'palette': ['red', 'yellow', 'green']}, 'Carbon Storage')
        Map.addLayer(roi, {'color': 'blue'}, 'Study Area')
        
        # Display the map
        Map.to_streamlit(height=400)
        
    except Exception as e:
        st.error(f"Error generating map: {str(e)}")

with col2:
    st.subheader("Carbon Storage Statistics")
    
    try:
        # Get area statistics
        stats = processor.get_area_statistics(roi, start_date, end_date)
        stats_dict = stats.getInfo()
        
        # Display statistics
        st.metric(
            "Average Carbon Storage",
            f"{stats_dict['NDVI']:.1f} tons/ha",
            delta=None
        )
        
        # Calculate total area (approximate)
        area = roi.area().getInfo() / 10000  # Convert to hectares
        total_carbon = stats_dict['NDVI'] * area
        
        st.metric(
            "Total Carbon Storage",
            f"{total_carbon:.0f} tons",
            delta=None
        )
        
    except Exception as e:
        st.error(f"Error calculating statistics: {str(e)}")

# Time series plot
st.subheader("Carbon Storage Over Time")
try:
    # Get time series data
    df = processor.create_time_series_data(roi, start_date, end_date)
    
    # Create the plot
    fig = px.line(
        df,
        x='Date',
        y='Carbon_Storage',
        title='Carbon Storage Trends',
        labels={'Carbon_Storage': 'Carbon Storage (tons/ha)'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
except Exception as e:
    st.error(f"Error generating time series: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Data source: Landsat 8 via Google Earth Engine</p>
    <p>Developed by Xunia Labs for TNC</p>
</div>
""", unsafe_allow_html=True) 