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
from transform import transform


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
datetime     = '2018-01-01T00:00:00Z/2018-02-15T23:00:00Z' # Begin/end yyyy-mm-ddThh:mm:ss
while True: # Extract and load loop
    extract.dbinfo(engine)
    dat = extract.dmi_api_get(baseurl, parameterIds, stations, datetime)
    # --- COMPLETE CODE HERE ---


# Check the extracted data by visualization with plotly
extract.check_dat(dat)


# Close the PostgreSQL database engine
engine.dispose()

