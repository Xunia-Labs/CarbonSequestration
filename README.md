# AI-Powered Carbon Sequestration Dashboard

This project creates a dashboard to estimate and visualize carbon sequestration in TNC-protected forest areas using satellite imagery and AI.

## Features
- Satellite imagery analysis using Google Earth Engine
- NDVI-based carbon sequestration estimation
- Interactive dashboard with maps and time series data
- Focus on Berkshire Taconic Landscape in Massachusetts

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Google Earth Engine:
- Sign up for a Google Earth Engine account at https://earthengine.google.com/
- Authenticate using:
```bash
earthengine authenticate
```

3. Run the dashboard:
```bash
streamlit run app.py
```

## Project Structure
- `app.py`: Main Streamlit dashboard application
- `data_processor.py`: Satellite data processing and analysis
- `requirements.txt`: Project dependencies

## Data Sources
- Satellite imagery: Google Earth Engine (Landsat 8)
- Forest carbon data: NDVI-based estimation
- Area boundaries: TNC protected areas 