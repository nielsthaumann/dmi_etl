
from geopy.geocoders import Nominatim
import numpy as np
import plotly.express as px
import plotly.io as pio
import requests
import pandas as pd

def weather_app(street_address, stations, engine): 
    '''
        Simple weather app using custom API server
        
        Syntax:    weather_app(street_address, stations, engine)
          
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
        
        print(f"Showing the temperature data from the nearest station at {nearname}.")
        r = requests.get(f"http://127.0.0.1:8000/measurements/stats_mean_temp?location_longitude={longitude}&location_latitude={latitude}")
        
        rows = [row for row in r.json() if row and "month_day_hour" in row]
        
        df = pd.DataFrame(rows)[["month_day_hour", "min_mean_temp", "avg_mean_temp", "max_mean_temp"]]
        df["month_day_hour"] = pd.to_datetime(df["month_day_hour"])
        df = df.sort_values("month_day_hour").reset_index(drop=True)

        pio.renderers.default = 'browser'
        fig = px.line(df, x='month_day_hour', 
                      y=['min_mean_temp', 'avg_mean_temp', 'max_mean_temp'], 
                      title=f"Temperature normals at {nearname} weather station near {street_address}", 
                      labels={'value': 'Temperature (°C)',
                              'variable': 'Statistic',
                              'month_day_hour': 'Date and time'},
                      color_discrete_map={
                          'min_mean_temp': 'blue',
                          'avg_mean_temp': 'green',
                          'max_mean_temp': 'red',
                      })
        # Rename the legend entries
        names = {'min_mean_temp': 'Minimum',
                 'avg_mean_temp': 'Average',
                 'max_mean_temp': 'Maximum'}
        fig.for_each_trace(lambda t: t.update(name=names[t.name]))
        fig.update_layout(legend_traceorder="reversed")
        fig.show(config={"scrollZoom": True})
        fig.write_html("temperature_normals.html", include_plotlyjs="cdn", config={"scrollZoom": True})