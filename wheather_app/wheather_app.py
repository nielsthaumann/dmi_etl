
from geopy.geocoders import Nominatim
import numpy as np
import plotly.express as px
import plotly.io as pio
import requests
import pandas as pd

def wheather_app(street_address, stations, engine): 
    '''
        Simple wheather app using the API server
        
        Syntax:    wheather_app(street_address, stations, engine)
          
    '''    
    
    geolocator = Nominatim(user_agent="dmi_etl_project")   # (user_agent is required, use any unique name)
    location = geolocator.geocode(street_address)        # Enter an address
    if location is not None:
        
        print(location.address)
        # print(location.latitude, location.longitude)
        
        # Find the nearest station coordinates
        query = """
        SELECT DISTINCT location_longitude, location_latitude
        FROM mean_temp
        ORDER BY location_latitude, location_longitude
        """
        db_locations = pd.read_sql(query, engine)
        dist = np.sqrt( (db_locations.location_longitude - location.longitude)**2 + ( db_locations.location_latitude - location.latitude)**2 )
        dist = np.nan_to_num(dist, nan=np.inf)
        min_id = np.argmin(dist)
        longitude = db_locations.location_longitude[min_id]
        latitude = db_locations.location_latitude[min_id]
        nearname = stations.name[(stations.longitude == str(longitude)) & (stations.latitude == str(latitude))].tolist()[0]
        
        print(f"Showing the mean temperature data from the nearest station at {nearname}.")
        r = requests.get(f"http://127.0.0.1:8000/measurements/mean_temp?location_longitude={longitude}&location_latitude={latitude}")
        time_to = [row["time_to"] for row in r.json()]
        values = [row["mean_temp"] for row in r.json()]
        df = pd.DataFrame({
            "time_to": pd.to_datetime(time_to),
            "mean_temp": values,
            })
        pio.renderers.default = 'browser'
        fig = px.line(df, x='time_to', y='mean_temp', title=f"Mean temperature at {nearname} wheather station near {street_address}")
        fig.show(config={"scrollZoom": True})
        