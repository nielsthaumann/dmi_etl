'''
    Unit tests for DMI ETL
'''


# Import required libraries
import unittest
from condb import condb
from extract import extract
import socket


# Connect to the PostgreSQL database
class TestDbCon(unittest.TestCase): 
    
    # Connecting to a non-existing location
    def test_non_existing_location(self):
        
        with self.assertRaises(condb.NonExistingLocation): 
            
            location = 'localhost:5000'
            dbname   = 'dmi_etl'
            _ = condb.condb(location, dbname)
    
    

# Mini web scraper for extracting information about stations from DMI's online table
class TestStationsScraper(unittest.TestCase): 
    
    # Requests errors
    # (Disable internet connection and exit by pressing Q)
    def test_stations_scraper_connection(self):
        
        with self.assertRaises(SystemExit): 
            
            _real_socket = socket.socket
            
            class _BlockedSocket(_real_socket):
                def connect(self, *args, **kwargs):
                    raise OSError("Network disabled for testing")
                connect_ex = connect
            
            socket.socket = _BlockedSocket
            URL = "https://www.dmi.dk/friedata/dokumentation/data/climate-data-stations"
            _ = extract.stations_scraper(URL)
            socket.socket = _real_socket
    
    # Table not found error
    def test_stations_scraper_table(self):
        
        with self.assertRaises(SystemExit): 
            
            URL = "https://www.dmi.dk/friedata/dokumentation/climate-data"
            _ = extract.stations_scraper(URL)


# Find the last time stamp extracted in the database and trusted for each measurement parameter
class TestLastTimeDb(unittest.TestCase): 
    
    # No output
    
    pass
    

# Extraction function for Climate Data API
class TestDmiApiGet(unittest.TestCase): 
    
    # No output
    
    pass


# Load extracted data into database
class TestToDb(unittest.TestCase): 
    
    # No loading
    
    pass


# Find the last time stamp extracted from the API
class TestLastTimeApi(unittest.TestCase): 
    
    # No output
    
    pass


# Transform the data
class TestTransform(unittest.TestCase): 
    
    # No output
    
    pass

# Create an API server with FastAPI and SQLModel
class TestApiServer(unittest.TestCase): 
    
    # No output
    
    pass


# Start the API server
class TestApiServerStart(unittest.TestCase): 
    
    # Fail
    
    pass



if __name__ == "__main__":
    unittest.main()
    
    
