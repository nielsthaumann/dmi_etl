'''
    Unit tests for DMI ETL
'''


# Import required libraries
import unittest
from extract import extract

# Mini web scraper for extracting information about stations from DMI's online table
class TestStationsScraper(unittest.TestCase): 
    
    # Requests errors
    # (Disable internet connection and exit by pressing Q)
    def TestStationsScraperConnection(self):
        
        with self.assertRaises(SystemExit): 
            
            URL = "https://www.dmi.dk/friedata/dokumentation/data/climate-data-stations"
            _ = extract.stations_scraper(URL)
    
    # Table not found error
    def TestStationsScraperTable(self):
        
        with self.assertRaises(SystemExit): 
            
            URL = "https://www.dmi.dk/friedata/dokumentation/climate-data"
            _ = extract.stations_scraper(URL)


# Find the last time stamp extracted in the database and trusted trusted for each measurement parameter
class TestLastTimeDb(unittest.TestCase): 
    
    # Create inspector object errors
    
    
    # No table names found in the database
    
    
    # No measurement station coordinates found in the database
    
    
    # Stations found with the mini web scraper are not found in the database, or vice versa
    
    
    # No last time stamp found in the database
    
    
    # Convert last time stamp in the database to ISO 8601 failed
    
    pass
    

# Extraction function for Climate Data API
class TestDmiApiGet(unittest.TestCase): 
    
    # No unique station Ids found
    
    
    # The start time (earliest time) stamp for the extraction is not a valid datetime format
    
    
    # Last time point in the database is not recognized by pandas
    
    
    # Request data via REST API errors
    
    
    # No json data were retrieved
    
    
    # No features were retrieved
    
    
    # Extract time from and to errors
    
    
    # Extract location errors
    
    
    # Extract measurement value errors
    
    
    # Extract measurement unit errors
    
    
    # Convert station data to a dataframe
    
    
    # Append station data to the list of dataframes
    
    
    # Ensure monotonously changing time series are extracted
    
    
    # Flatten the dataframes across stations errors
    
    pass


# Load extracted data into database
class TestToDb(unittest.TestCase): 
    
    # Write to the database errors
    
    pass


# Find the last time stamp extracted from the API
class TestLastTimeApi(unittest.TestCase): 
    
    # No data were extracted from the API
    
    
    # Convert last time stamp in the database to ISO 8601 failed
    
    pass


# Transform the data
class TestTransform(unittest.TestCase): 
    
    # Create inspector object errors
    
    
    # No table names found in the database
    
    
    # Calculate the average measurement values across years using SQL errors

    pass

# Create an API server with FastAPI and SQLModel
class TestApiServer(unittest.TestCase): 
    
    # Create inspector object errors
    
    
    # No table names found in the database
    
    
    # Create data models errors
    
    
    # Dependency that opens a database session for each request errors
    
    
    # Unknown measurement parameter from user API request
    
    
    # Longitude not found in database
    
    
    # Latitude not found in database
    
    
    # Execute session errors
    
    pass


# Start the API server
class TestApiServerStart(unittest.TestCase): 
    
    # Start the API server errors
    
    pass


# Stop the API server
class TestApiServerStop(unittest.TestCase): 
    
    # Stop the API server errors
    
    pass

