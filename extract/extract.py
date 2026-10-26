

'''
    Extract data from DMI APIs
    
'''

# Import required libraries
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import numpy as np
from datetime import datetime


def stations_scraper(): 
    '''
        stations = stations_scraper()
        
        Mini web scraper for extracting information about stations from DMI's online table
    '''
    
    
    print('\nMini web scraper for extracting stations from DMIs online table', end='...')
    
    URL = "https://www.dmi.dk/friedata/dokumentation/data/climate-data-stations"
    
    resp = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    
    # Parse HTML
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Find table
    textarea = soup.find("textarea", class_="dmi-input")
    text = textarea.get_text()   # or textarea.string
    
    # Convert to dataframe
    stations = pd.read_csv(
        StringIO(text.lstrip()),   # removes the leading \n, tab and spaces before "stationId"
        sep="\t",
        dtype=str,                 # keeps stationId as string
        keep_default_na=False,     # optional: empty cells stay "" instead of NaN
    )
    
    print(f" Found {len(stations['stationId'].unique())} stations.")
    
    return stations


# # Constrain to Aarhus Kommune ( Use: https://boundingbox.klokantech.com/ )
# bbox = [8.948564,55.995726,9.389087,56.330475]

def loc_range(bbox, stations): 
    '''
        stations = loc_range(bbox, stations)
        
        Location contraint
    '''
    
    # Extract latitudes and longitudes
    lat = pd.to_numeric(stations['latitude'],  errors='coerce')
    lon = pd.to_numeric(stations['longitude'], errors='coerce')
    
    # Create latitudes and longitudes mask
    inside = lat.between(bbox[1], bbox[3]) & lon.between(bbox[0], bbox[2])
    
    # Apply latitudes and longitudes mask
    stations = stations.loc[inside].reset_index(drop=True)
    
    print(f'Constrained to {len(stations['stationId'].unique())} stations wihtin bbox={bbox}.')
    
    return stations 


def dmi_api_get(baseurl, stations, parameterIds, unit_mapping, start_time, last_time_db, params_stationId): 
    
    '''
        dat, station_params = dmi_api_get(baseurl, stations, parameterIds, unit_mapping, start_time, last_time_db, params_stationId)
        
        Extraction function for Climate Data API
    '''
    
    # Find unique station Ids
    stationIds = stations['stationId'].unique()
    
    # Prepare a list of pandas dataframes with extracted data ( dat[parameter] )
    dat = [[] for _ in parameterIds]
    
    # Loop over parameters
    for i, parameterId in enumerate(parameterIds): 
        
        print(f'\n📏 Extracting {parameterId} data...')
        
        # Prepare a list for extracted station data ( station_dat[station] )
        station_dat = [None]*len(stationIds)
        
        # Loop over stations
        for j, stationId in enumerate(stationIds):
            
            print(f'\t📡 Extracting {parameterId} data from station {j+1} of {len(stationIds)}...')
            
            # Add one month to the last time point in the database and format it as an ISO 8601 string with a trailing Z (UTC)
            end_time = (pd.Timestamp(last_time_db) + pd.DateOffset(months=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Define the time range for the API request
            date_time = start_time +'/' + end_time # Begin/end yyyy-mm-ddThh:mm:ss
            
            # If this parameter has been extracted before
            if last_time_db > start_time: # (The last time stamp in the database is later than the initial start time for the API requests)
                
                # If the station is not trusted for this measurement parameter
                if not stationId in params_stationId[parameterId]: 
                    
                    print(f'\t\t\t🟡 Skipping station, since no {parameterId} data found on first request.')    
                    continue
            
            print(f'\t\t🕒 Requesting data from the month of {datetime.fromisoformat(last_time_db):%B %Y}...')
            
            # Define parameter, station, time range, and time resolution for query
            params = {'parameterId': parameterId, # Measurement parameter.
                      'stationId': stationId,     # Station Id.
                      'datetime': date_time,      # Time range.
                      'timeResolution': 'hour',   # Ensure hour sampling rate.
                      'limit': 1000}              # With limit=1000, one month of data would be feasible to extract.
            
            json = {} # Prepare a dictionary for json objects
            
            # Request data via REST API
            try: 
                r = requests.get(baseurl, params)
                
            except requests.exceptions.HTTPError as errh:
                print('HTTP Error:', errh)
            except requests.exceptions.ConnectionError as errc:
                print('Connection Error:', errc)
            except requests.exceptions.Timeout as errt:
                print('Timeout Error:', errt)
            except requests.exceptions.RequestException as err:
                print('Something Else:', err)
                
            json = r.json() # Extract the json objects
            if json == {}:
                print('\t\t\t🔴 No json data were retrieved.')
            else: 
                
                # If json objects were retrieved
                if r.status_code==200: 
                
                    n = len(json['features']) # Number of json objects?
                    
                    if n==0:  # If there are no json objects
                        
                        print('\t\t\t🔴 No features were retrieved.')
                        
                    else: 
                        
                        # Prepare a dictionary for the extracted time, location, and meaasurement value
                        station_dat[j]   = {'time_from':          [[] for _ in range(n)], # RFC3339 5.6
                                            'time_to':            [[] for _ in range(n)], # RFC3339 5.6
                                            'location_longitude': [[] for _ in range(n)], # Longitude in WGS84
                                            'location_latitude':  [[] for _ in range(n)], # Latitude in WGS84
                                            parameterId:          [[] for _ in range(n)], # Measurement value
                                            'unit':               [[] for _ in range(n)]} # Measurement unit
                        
                        for t in range(n): # Loop over time stamps
                            
                            # Extract time from
                            try:
                                
                                station_dat[j]['time_from'][t] = json['features'][t]['properties']['from'] # RFC3339 5.6
                            
                            except TypeError as e:
                                if "'NoneType' object is not subscriptable" in str(e):
                                    continue  # Skip missing data
                                else:
                                    raise  # Re-raise unrelated TypeErrors
                            
                            # Extract time to
                            try: 
                                
                                station_dat[j]['time_to'][t] = json['features'][t]['properties']['to'] # RFC3339 5.6
                            
                            except TypeError as e:
                                if "'NoneType' object is not subscriptable" in str(e):
                                    continue  # Skip missing data
                                else:
                                    raise  # Re-raise unrelated TypeErrors
                            
                            # Extract location longitude
                            try: 
                                station_dat[j]['location_longitude'][t] = json['features'][t]['geometry']['coordinates'][0] # Longitude in WGS84
                            except TypeError as e:
                                if "'NoneType' object is not subscriptable" in str(e):
                                    continue  # Skip missing data
                                else:
                                    raise  # Re-raise unrelated TypeErrors
                            
                            # Extract location latitude
                            try: 
                                station_dat[j]['location_latitude'][t] = json['features'][t]['geometry']['coordinates'][1] # Latitude in WGS84
                            except TypeError as e:
                                if "'NoneType' object is not subscriptable" in str(e):
                                    continue  # Skip missing data
                                else:
                                    raise  # Re-raise unrelated TypeErrors
                            
                            # Extract measurement value
                            try: 
                                station_dat[j][parameterId][t] = json['features'][t]['properties']['value']
                            except TypeError as e:
                                if "'NoneType' object is not subscriptable" in str(e):
                                    continue # Skip missing data
                                else:
                                    raise  # Re-raise unrelated TypeErrors
                                    
                            # Add measurement unit
                            station_dat[j]['unit'][t] = unit_mapping[parameterId]
            
            if station_dat[j]:                            # If station data were retrieved
                
                print('\t\t\t✅ Completed.')
                
                station_df = pd.DataFrame(station_dat[j]) # Convert station data to a dataframe
                dat[i].append(station_df)                 # Append station data to the list of dataframes
                
                # Ensure monotonously changing time series are extracted
                hourdiff = np.max(np.diff(pd.to_datetime(station_df['time_to'])) / pd.Timedelta(hours=1))
                if hourdiff < -1: 
                    print(f'\t\t\t🟡 Warning: Data from {hourdiff} hours were missing.')
        
        # Flatten the dataframes across stations
        if dat[i]:
            dat[i] = pd.concat(dat[i], ignore_index=True)
            
        else:
            print(f'\t\t🔴 No data retrieved for {parameterId}.')
            dat[i] = pd.DataFrame()
        
        print(f'✅ Completed extracting {parameterId} data.')
    
    # Output all extracted data
    return dat


def check_dat(dat, parameterIds): 
    '''
        check_dat(dat)
        
        Check the extracted data by visualization with plotly
    '''
    
    # See: https://plotly.com/python/builtin-colorscales/
    color_mapping = {
                    'mean_temp':         'thermal',
                    'mean_relative_hum': 'teal',
                    'mean_wind_speed':   'hot',
                    'bright_sunshine':   'solar',
                    'mean_radiation':    'inferno',
                    'mean_cloud_cover':  'greys',
                    'acc_precip':        'plotly3',
                    'snow_depth':        'ice'
                    }
    
    import plotly.express as px
    import plotly.io as pio
    pio.renderers.default = 'browser'
    
    for i in range(len(dat)):  # Loop over features
        
        try: 
            
            # Copy plotting data to a new dataframe
            df = pd.DataFrame({
                'Longitude':     dat[i]['location_longitude'],
                'Latitude':      dat[i]['location_latitude'],
                'Time':          pd.to_datetime(dat[i]['time_to'], utc=True, errors="coerce"),
                parameterIds[i]: dat[i][parameterIds[i]], 
            })
            
            # Define the color scale and unit for plotting
            colscale = color_mapping[parameterIds[i]]
            unit = dat[i]['unit'].drop_duplicates().squeeze()
            
            # Create the figure
            fig = px.scatter_3d(df, x='Longitude', y='Latitude', z='Time', color=parameterIds[i], 
                                color_continuous_scale=colscale, 
                                title=f'Extracted {parameterIds[i]} data from DMI API')
            
            fig.update_traces(marker=dict(size=3))
            fig.update_scenes(xaxis_autorange="reversed")   # Inverted x axis
            fig.update_scenes(yaxis_autorange="reversed")   # Inverted y axis
            fig.update_layout(coloraxis_colorbar=dict(title=unit))  # Colorbar unit
            
            fig.write_html(f'dmi_api_{parameterIds[i]}.html') # Write the figure to an html file
            fig.show() # Open the figure in the default browser
    
        except Exception as e:
            
            print(f'An error occurred while creating dmi_api_{parameterIds[i]}.html plot: {e}')


def last_time_api(dat): 
    '''
        last_time_api = extract.last_time_api(dat)
        
        Find the last time stamp extracted from the API
    '''
    
    last_time_api = []
    
    for i in range(len(dat)): # Loop over measurement parameters
        
        # Find the last time stamp extracted
        if not dat[i].empty: 
            
            last_time_api.append(dat[i]['time_to'].max())
    
    times = pd.to_datetime(last_time_api)
    last_time_api = times.max().isoformat()

    
    return last_time_api

