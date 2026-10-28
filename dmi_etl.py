'''
    DMI ETL main routine launcher
'''


# Import modules
from condb import condb
from extract import extract
from load import load
from transform import transform
from api import api
import uvicorn
from weather_app.weather_app import weather_app
import threading
import pandas as pd
from datetime import datetime
from time import time


# Connect to the PostgreSQL database
# (NB: Remember to start the server on Docker)
# ( https://docs.sqlalchemy.org/en/21/intro.html )
location = 'localhost:5432'
dbname   = 'dmi_etl'
engine = condb.condb_ui(location, dbname)


# Find available stations
URL = "https://www.dmi.dk/friedata/dokumentation/data/climate-data-stations"
stations = extract.stations_scraper(URL)


# # Constrain location ( Use: https://boundingbox.klokantech.com/ )
# bbox = [8.948564,55.995726,9.389087,56.330475] # Aarhus Kommune 
# Constrain to Denmark ( Use: https://boundingbox.klokantech.com/ )


# Extract data from DMI APIs
baseurl      = 'https://opendataapi.dmi.dk/v2/climateData/collections/stationValue/items'

parameterIds = ['mean_temp', 
                'mean_relative_hum', 
                'mean_wind_speed', 
                'bright_sunshine', 
                'mean_radiation', 
                'mean_cloud_cover', 
                'acc_precip', 
                'snow_depth']

unit_mapping =    {
                  'mean_temp':         '°C',    # Mean temperature °C
                  'mean_relative_hum': '%',     # Mean relative humidity %
                  'mean_wind_speed':   'm/s',   # Mean wind speed m/s
                  'bright_sunshine':   'Minutes/hours' , # Minutes/hours of bright sunshine
                  'mean_radiation':    'W/m²',           # Mean radiation (spectral range: 305-2800nm) W/m²
                  'mean_cloud_cover':  '%',     # Cloud cover %
                  'acc_precip':        'mm',    # Accumulated precipitation mm
                  'snow_depth':        'cm',    # Snow depth cm
                  }

# Define the start time stamp, start_time. 
# Extract and load loop will run from the start time stamp 
# until the latest available time stamp has been extracted and loaded. 
start_time = '2015-01-01T00:00:00Z'
station_params = []

while True: # Extract and load loop
    
    clock_start = time()
    
    print('\n🔃 Checking for new data on the API not loaded to the database...')
    
    # Find the last time stamp extracted in the database
    last_time_db, params_stationId = condb.last_time_db(engine, start_time, stations, parameterIds)
    
    # Extract new data from the DMI API
    dat = extract.dmi_api_get(baseurl, stations, parameterIds, unit_mapping, start_time, last_time_db, params_stationId)
    
    # Check the extracted data by visualization with plotly
    # extract.check_dat(dat, parameterIds)
    
    # Check whether any new time stamps were extracted
    if not all(len(x) == 0 for x in dat): 
        
        # Find the last time stamp extracted from the API
        last_time_api = extract.last_time_api(dat)
        
        if not last_time_api==last_time_db: 
        
            # Load the new data into the PostgreSQL database
            load.to_db(engine, parameterIds, dat)

        else: # If no new data was extracted, exit the extract and load loop
            
            print('\n🔃 The database is up to date!') 
            
            dbsize = pd.read_sql( "SELECT pg_size_pretty(pg_database_size('dmi_etl')) AS size", engine)['size'][0]
            
            print(f'\n🗄️ {dbsize} are occupied on {location} for storing data between {datetime.fromisoformat(start_time):%B %Y} and {datetime.fromisoformat(last_time_db):%B %Y}.')
            
            break
        
    clock_end = time()
    
    minperyear = (clock_end - clock_start) / 60 * 12
    
    print(f'\n⏳ The current processing speed is ~{round(minperyear,1)} minutes per year of data.')
        

# Transform the data and upload the result to stats_{parameter_Id} tables
transform.transform(engine)


# Create an API server with FastAPI and SQLModel
app = api.api_server(engine)

# Start the API server
config = uvicorn.Config(app, host="127.0.0.1", port=8000)
server = uvicorn.Server(config)
thread = threading.Thread(target=server.run, daemon=True)
thread.start()

# Mini app on the API
street_address = 'Kannikegade 18'
# street_address = 'Lautruphøj 1-3 A, Ballerup'
# street_address = 'Dannebrogsgade 2, Odense'
weather_app(street_address, stations, engine)

# Stop the API server
server.should_exit = True   # ask uvicorn to stop gracefully
thread.join()               # wait until it has finished

# Close the PostgreSQL database engine
engine.dispose()


    