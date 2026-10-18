'''
    DMI ETL
'''


# Indsamling af miljødata: 

# - API med vejr data fra Aarhus ( https://www.dmi.dk/frie-data ). 

# Nemmere at gennemse API data med nushell i stedet for json pretty print. 

# Rettelser: 

# dat = [[None]]*len(parameterIds)
# 
# giver flere referencer til det samme liste-objekt.
# Desuden starter hver liste med [None] og ikke en tom liste. 
# For at lave seperate kopier af den samme tomme liste, brug list comprehension syntax: 
# 
# dat = [[] for _ in parameterIds]

# Hvis alle elementer er None, kaster pd.concat ValueError: All objects passed were None. 
# Løs ved at sikre at den undtagelse ikke er tilfældet.
#
# dat[i] = pd.concat(dat[i], ignore_index=True)
#
# rettes til: 
#
# if dat[i]:
#     dat[i] = pd.concat(dat[i], ignore_index=True)
# else:
#     print(f'No data retrieved for {parameterId}.')
#     dat[i] = pd.DataFrame()
# 
# Use built in pd.to_numeric instead of astype('float'), 
# where empty cells are kept as empty strings ('')

# Import modules
from condb import condb
from extract import extract
from load import load
# from transform import transform


# Connect to the PostgreSQL database
# ( https://docs.sqlalchemy.org/en/21/intro.html )
# --- ADD USER PROMPT HERE ---
username = 'nth'
password = 'pass'
location = 'localhost:5432'
dbname   = 'dmi_etl'
# ---- # 
engine = condb.condb(username, password, location, dbname)


# Find available stations
stations = extract.stations_scraper()


# Constrain to Aarhus Kommune ( Use: https://boundingbox.klokantech.com/ )
bbox = [8.948564,55.995726,9.389087,56.330475]
stations = extract.loc_range(bbox, stations)


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
start_time = '2018-01-01T00:00:00Z'

while True: # Extract and load loop
    
    # Find the last time stamp extracted for each measurement parameter and location in the database
    last_time = condb.last_time(engine)
    
    # Extract new data from the DMI API
    dat = extract.dmi_api_get(baseurl, stations, parameterIds, unit_mapping, start_time, last_time)
    
    # Check the extracted data by visualization with plotly
    # extract.check_dat(dat, parameterIds)
    
    # Check whether any new time stamps were extracted
    if not all(len(x) == 0 for x in dat): 
    
        # Load the new data into the PostgreSQL database
        load.to_db(engine, parameterIds, dat)
        
    else: # If no new data was extracted, exit the extract and load loop
        
        break
    

# Close the PostgreSQL database engine
engine.dispose()

