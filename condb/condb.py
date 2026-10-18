'''
    Connect to PostgreSQL database
'''

# Import required libraries
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine, inspect
import pandas as pd

def condb(username, password, location, dbname): 
    '''
        engine = condb(username, password, location, dbname)
        
        Connect to a database
    '''
    
    url = 'postgresql+psycopg://' + username + ':' + password + '@' + location + '/'+ dbname
    
    # Check if database already exists or needs to be created
    if not database_exists(url):
        
        create_database(url)
    
    # Connect to the database
    engine = create_engine(url)
    
    return engine

def last_time(engine): 
    '''
        last_time = condb.last_time(engine)
        
        Find the last time stamp extracted for each measurement parameter and location in the database
    '''
    
    # Create an inspector object
    inspector = inspect(engine)
    
    # Get a list of table names indicating each measurement parameter
    db_parameterIds = inspector.get_table_names()
    
    # Prepare a dictionary of dataframes with locations and last time stamp extracted
    last_time = dict()
    
    for i in range(len(db_parameterIds)): # Loop over measurement parameters
        
        cols = pd.read_sql(f"SELECT * FROM {db_parameterIds[i]} LIMIT 0", engine).columns.tolist()
        last_time[db_parameterIds[i]] = pd.DataFrame(columns=cols)
        
        db_locations = pd.read_sql(f'SELECT DISTINCT location_longitude, location_latitude FROM {db_parameterIds[i]}', engine)
        
        for j in range(len(db_locations)): # Loop over locations
            
            # Find the last time stamp extracted from each location
            db_location = db_locations['location_longitude'][j], db_locations['location_latitude'][j]
            last_time[db_parameterIds[i]].loc[len(last_time[db_parameterIds[i]])] = pd.read_sql(f"SELECT * FROM {db_parameterIds[i]} WHERE location_longitude={db_location[0]} AND location_latitude={db_location[1]} ORDER BY time_to DESC LIMIT 1", engine).loc[0]
            
    return last_time

