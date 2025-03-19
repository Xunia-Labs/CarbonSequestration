import ee
import geemap
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class CarbonSequestrationProcessor:
    def __init__(self):
        # Initialize Earth Engine
        try:
            ee.Initialize()
        except:
            try:
                ee.Authenticate()
                ee.Initialize()
            except Exception as e:
                print(f"Error initializing Earth Engine: {str(e)}")
                raise

    def get_ndvi_time_series(self, roi, start_date, end_date):
        """
        Get NDVI time series for a region of interest
        """
        # Define the Landsat 8 collection
        collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                     .filterBounds(roi)
                     .filterDate(start_date, end_date)
                     .sort('CLOUD_COVER'))

        def add_ndvi(image):
            # Calculate NDVI
            nir = image.select('SR_B5')
            red = image.select('SR_B4')
            ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
            return image.addBands(ndvi)

        # Map the NDVI calculation over the collection
        with_ndvi = collection.map(add_ndvi)
        
        # Get the NDVI band
        ndvi_collection = with_ndvi.select('NDVI')
        
        return ndvi_collection

    def estimate_carbon_storage(self, ndvi):
        """
        Estimate carbon storage based on NDVI
        Using a simplified model: Carbon (tons/ha) = NDVI * 200
        """
        # Convert NDVI to carbon storage (simplified model)
        carbon = ndvi.multiply(200)
        return carbon

    def get_area_statistics(self, roi, start_date, end_date):
        """
        Get carbon sequestration statistics for the area
        """
        # Get NDVI time series
        ndvi_series = self.get_ndvi_time_series(roi, start_date, end_date)
        
        # Calculate mean NDVI
        mean_ndvi = ndvi_series.mean()
        
        # Estimate carbon storage
        carbon_storage = self.estimate_carbon_storage(mean_ndvi)
        
        # Calculate statistics
        stats = carbon_storage.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=30,
            maxPixels=1e9
        )
        
        return stats

    def create_time_series_data(self, roi, start_date, end_date):
        """
        Create time series data for visualization
        """
        # Get NDVI time series
        ndvi_series = self.get_ndvi_time_series(roi, start_date, end_date)
        
        # Create a list to store results
        dates = []
        carbon_values = []
        
        # Get the number of images
        count = ndvi_series.size().getInfo()
        
        # Process each image
        for i in range(count):
            image = ee.Image(ndvi_series.toList(count).get(i))
            date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd').getInfo()
            
            # Calculate carbon storage for this image
            carbon = self.estimate_carbon_storage(image)
            stats = carbon.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=30,
                maxPixels=1e9
            )
            
            dates.append(date)
            carbon_values.append(stats.getInfo()['NDVI'])
        
        # Create DataFrame
        df = pd.DataFrame({
            'Date': dates,
            'Carbon_Storage': carbon_values
        })
        
        return df

# Example usage
if __name__ == "__main__":
    # Define the Berkshire Taconic Landscape region (example coordinates)
    roi = ee.Geometry.Rectangle([-73.5, 42.0, -73.0, 42.5])
    
    # Initialize processor
    processor = CarbonSequestrationProcessor()
    
    # Get statistics for the last year
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    stats = processor.get_area_statistics(roi, start_date, end_date)
    print("Carbon Storage Statistics:", stats.getInfo()) 