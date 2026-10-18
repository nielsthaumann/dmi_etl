

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
    
    textarea = soup.find("textarea", class_="dmi-input")
    
    text = textarea.get_text()   # or textarea.string
    
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
    
    lat = pd.to_numeric(stations['latitude'],  errors='coerce')
    lon = pd.to_numeric(stations['longitude'], errors='coerce')
    inside = lat.between(bbox[1], bbox[3]) & lon.between(bbox[0], bbox[2])
    stations = stations.loc[inside].reset_index(drop=True)
    
    print(f'Constrained to {len(stations['stationId'].unique())} stations wihtin bbox={bbox}.')
    
    return stations 


# Retrive data for new time points that are not already available in the database
# datetime = '2018-02-12T00:00:00Z/2018-03-18T00:00:00Z' # Begin/end yyyy-mm-ddThh:mm:ss

# Handle requests objects limit by increasing the datetime offset: 
# > DMI Climate Data API uses <begin>/<end> syntax and wildcards ..
#   The following syntax creates a datatime offset request: ?datetime=yyyy-mm-ddThh:mm:ss/..


#   - Temperatur, luftfugtighed, vindhastighed, sollys, stråling, skydække, regn, sne. 
# 	  
#     https://www.dmi.dk/friedata/dokumentation/apis/climate-data-api-1
#     https://www.dmi.dk/friedata/dokumentation/climate-data#c24284
#     https://www.dmi.dk/friedata/dokumentation/climate-data#c24290
# 
#     ( https://www.dmi.dk/friedata/dokumentation/meteorological-observation-api )
# 

# baseurl = 'https://opendataapi.dmi.dk/v2/climateData/collections/stationValue/items'

# parameterIds = ['mean_temp', 
#                 'mean_relative_hum', 
#                 'mean_wind_speed', 
#                 'bright_sunshine', 
#                 'mean_radiation', 
#                 'mean_cloud_cover', 
#                 'acc_precip', 
#                 'snow_depth']

# unit_mapping =    {
#                   'mean_temp':         '°C',    # Mean temperature °C
#                   'mean_relative_hum': '%',     # Mean relative humidity %
#                   'mean_wind_speed':   'm/s',   # Mean wind speed m/s
#                   'bright_sunshine':   'Minutes/hours' , # Minutes/hours of bright sunshine
#                   'mean_radiation':    'W/m²',           # Mean radiation (spectral range: 305-2800nm) W/m²
#                   'mean_cloud_cover':  '%',     # Cloud cover %
#                   'acc_precip':        'mm',    # Accumulated precipitation mm
#                   'snow_depth':        'cm',    # Snow depth cm
#                   }

# # Define the start time stamp, start_time. 
# # Data is extracted from the start time stamp until the latest available time stamp. 
# start_time = '2018-01-01T00:00:00Z'

def dmi_api_get(baseurl, stations, parameterIds, unit_mapping, start_time, last_time): 
    
    '''
        dat = dmi_api_get(baseurl, stations, parameterIds, unit_mapping, start_time, last_time)
        
        Extraction function for Climate Data API
    '''
    
    stationIds = stations['stationId'].unique()
    
    # Prepare a list of pandas dataframes with extracted data ( dat[parameter] )
    dat = [[] for _ in parameterIds]
    
    # Loop over parameters
    for i, parameterId in enumerate(parameterIds): 
        
        print(f'\n📏 Extracting {parameterId} data...')
        
        # Prepare a list of pandas dataframes for extracted station data ( station_dat[station] )
        station_dat = [None]*len(stationIds)
        
        # Loop over stations
        for j, stationId in enumerate(stationIds):
            
            print(f'\t📡 Extracting {parameterId} data from station {j+1} of {len(stationIds)}...')
            
            # Default start from the global start time (used if no earlier data is found)
            time_stamp = start_time
            
            # Find the current station in the stations table
            station = stations[stations.stationId == stationId]
            
            # If this parameter has been extracted before
            # and the station exists in the stations table
            if parameterId in last_time and not station.empty:
                
                # Search for earlier timestamps
                
                # Take the station's coordinates as plain floats
                lon, lat = map(float, station[['longitude', 'latitude']].iloc[0])
                
                # Previously extracted data for this parameter
                lt = last_time[parameterId]
                
                # Boolean mask: rows whose coordinates match this station (np.isclose avoids float equality problems)
                mask = np.isclose(lt['location_longitude'], lon) & np.isclose(lt['location_latitude'], lat)
                
                # Only override the default if at least one matching row exists
                if mask.any():
                    time_stamp = lt.loc[mask, 'time_to'].max()
            
            # Add one month to the starting point and format it as an ISO string with a trailing Z (UTC)
            end_time = (pd.Timestamp(time_stamp) + pd.DateOffset(months=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            date_time = start_time +'/' + end_time # Begin/end yyyy-mm-ddThh:mm:ss
            
            print(f'\t\t🕒 Requesting data from the month of {datetime.fromisoformat(time_stamp):%B %Y}...')
            
            # Define parameter, station, time range, and time resolution for query
            params = {'parameterId': parameterId, # Measurement parameter.
                      'stationId': stationId,     # Station Id.
                      'datetime': date_time,       # Time range.
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
                        
                        # Prepare a dictionary for extracted data
                        station_dat[j]   = {'time_from':          [[] for _ in range(n)], # RFC3339 5.6
                                            'time_to':            [[] for _ in range(n)], # RFC3339 5.6
                                            'location_longitude': [[] for _ in range(n)], # Longitude in WGS84
                                            'location_latitude':  [[] for _ in range(n)], # Latitude in WGS84
                                            parameterId:          [[] for _ in range(n)], # Measurement parameter
                                            'unit':               [[] for _ in range(n)]} # Measurement unit
                        
                        for t in range(n): # Loop over time stamps
                            
                            # Extract time, location, and meaasurement value: 
                            
                            # Extract time
                            try:
                                station_dat[j]['time_from'][t] = json['features'][t]['properties']['from'] # RFC3339 5.6
                            except TypeError as e:
                                if "'NoneType' object is not subscriptable" in str(e):
                                    continue  # Skip missing data
                                else:
                                    raise  # Re-raise unrelated TypeErrors
                            try: 
                                station_dat[j]['time_to'][t] = json['features'][t]['properties']['to'] # RFC3339 5.6
                            except TypeError as e:
                                if "'NoneType' object is not subscriptable" in str(e):
                                    continue  # Skip missing data
                                else:
                                    raise  # Re-raise unrelated TypeErrors
                            
                            # Extract location
                            try: 
                                station_dat[j]['location_longitude'][t] = json['features'][t]['geometry']['coordinates'][0] # Longitude in WGS84
                            except TypeError as e:
                                if "'NoneType' object is not subscriptable" in str(e):
                                    continue  # Skip missing data
                                else:
                                    raise  # Re-raise unrelated TypeErrors
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
                
                station_df = pd.DataFrame(station_dat[j]) # Convert it to a dataframe
                dat[i].append(station_df)                 # Append it to the list of dataframes
                
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

