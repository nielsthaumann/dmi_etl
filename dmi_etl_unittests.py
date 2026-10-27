'''
    Unit tests for DMI ETL
'''


# Import required libraries
import unittest
from condb import condb
from extract import extract
from load import load
from transform import transform
import socket
import pandas as pd
from unittest import mock


# Connect to the PostgreSQL database
class TestDbCon(unittest.TestCase): 
    
    # Connecting to a non-existing location
    def test_non_existing_location(self):
        
        with self.assertRaises(condb.NonExistingLocation): 
            
            """Verifying that NonExistingLocation exception is raised."""
            
            location = 'localhost:5000'
            dbname   = 'dmi_etl'
            _ = condb.condb(location, dbname)
    

# Mini web scraper for extracting information about stations from DMI's online table
class TestStationsScraper(unittest.TestCase): 
    
    # Requests errors
    # (Disable internet connection and exit by pressing Q)
    def test_stations_scraper_connection(self):
        
        with self.assertRaises(SystemExit): 
            
            """Verifying that disabled internet connection is handled."""
            
            _real_socket = socket.socket
            
            class _BlockedSocket(_real_socket):
                def connect(self, *args, **kwargs):
                    raise OSError("Network disabled for testing")
                connect_ex = connect
            
            socket.socket = _BlockedSocket
            URL = "https://www.dmi.dk/friedata/dokumentation/data/climate-data-stations"
            try:
                _ = extract.stations_scraper(URL)
            finally:
                socket.socket = _real_socket
    
    # Table not found error
    def test_stations_scraper_table(self):
        
        with self.assertRaises(SystemExit): 
            
            """Verifying that failure to read DMI's online table is stated."""
            
            URL = "https://www.dmi.dk/friedata/dokumentation/climate-data"
            _ = extract.stations_scraper(URL)


location = 'localhost:5432'
dbname   = 'dmi_etl'
engine = condb.condb_ui(location, dbname)

# Find available stations
URL = "https://www.dmi.dk/friedata/dokumentation/data/climate-data-stations"
stations = extract.stations_scraper(URL)

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

start_time = '2015-01-01T00:00:00Z'
station_params = []

# Find the last time stamp extracted in the database
last_time_db, params_stationId = condb.last_time_db(engine, start_time, stations, parameterIds)


# Find the last time stamp extracted in the database and valid for each measurement parameter
class TestLastTimeDb(unittest.TestCase): 
    
    # Verify outputs
    def test_last_time_db(self): 
        
        """Ensuring a datetime class as output from condb.last_time_db."""
        
        self.assertEqual(type(pd.to_datetime(last_time_db)), pd.Timestamp)
        
        """Ensuring a dictionary with the parameterIds as keys as output from condb.last_time_db."""
        
        self.assertEqual(list(params_stationId.keys()), parameterIds)
    

# Extract new data from the DMI API
print('\n🔃 Checking for new data on the API not loaded to the database...')
dat = extract.dmi_api_get(baseurl, stations, parameterIds, unit_mapping, start_time, last_time_db, params_stationId)


# Extraction function for Climate Data API
class TestDmiApiGet(unittest.TestCase): 
    
    # Verify outputs
    def test_dmi_api_get(self): 
        
        """Ensuring to get a list pf pandas dataframes as output from extract.dmi_api_get."""
        
        self.assertIsInstance(dat, list)
        self.assertTrue(all(isinstance(df, pd.DataFrame) for df in dat))


# Find the last time stamp extracted from the API
last_time_api = extract.last_time_api(dat)

# Find the last time stamp extracted from the API
class TestLastTimeApi(unittest.TestCase): 
    
    # Verify outputs
    def test_last_time_api(self): 
        
        """Ensuring a datetime class as output from extract.last_time_api."""
        
        self.assertEqual(type(pd.to_datetime(last_time_api)), pd.Timestamp)
    

# Load extracted data into database
class TestToDb(unittest.TestCase): 
    
    # Ensure mock loading works
    def test_load_to_db(self): 
        
        """Ensuring that mock Loading of extracted data into database works."""
        
        with mock.patch.object(pd.DataFrame, "to_sql") as m:
            load.to_db(engine, parameterIds, dat)
            expected = sum(not df.empty for df in dat)
            self.assertEqual(m.call_count, expected)


# Transform the data
class TestTransform(unittest.TestCase): 
    
    class TestTransform(unittest.TestCase):
        
        def test_transform(self):
            
            """Ensuring that transform.transform runs without error."""
            
            try:
                transform.transform(engine)
                
            except Exception as e:
                
                self.fail(f"transform.transform raised {type(e).__name__}: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
    
    
