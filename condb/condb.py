'''
    Connect to PostgreSQL database
'''

# Import required libraries
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine, inspect
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import OperationalError
import tkinter as tk
from tkinter import simpledialog, messagebox
import socket


def condb(location, dbname): 
    '''
        Connect to a database
        
        Syntax: 
            
            engine = condb(location, dbname)
        
    '''
    
    # Check if the location exists
    timeout = 3
    host, sep, port = location.rpartition(":")
    try: 
        
        socket.create_connection(address = (host, port), timeout=timeout)
        
    except:
        
        print(f"Failed connecting to {location}.")
        
        raise SystemExit("Login cancelled")
    
    # User interface for connecting to database
    def condb_ui(): 
        
        username = simpledialog.askstring("User name", prompt='Please enter a valid user name:')
        password = simpledialog.askstring("Password", prompt='Please enter a valid password:', show="*")
        
        return username, password
    
    username, password = condb_ui()
    
    url = 'postgresql+psycopg://' + username + ':' + password + '@' + location + '/'+ dbname
    
    # Check if database already exists or needs to be created
    if not database_exists(url):
        
        print(f"The database '{dbname}' does not exist. Creating it. ")
        create_database(url)
    
    # Connect to the database
    engine = create_engine(url)    

    return engine    
    

def last_time_db(engine, start_time, stations, parameterIds): 
    '''
        
    Find the last time stamp extracted in the database and trusted trusted for each measurement parameter
    
    Syntax: 
        
        last_time_db, params_stationId = condb.last_time_db(engine, start_time, stations, parameterIds)
        
    '''
    
    # Create an inspector object
    inspector = inspect(engine)
    
    # Get a list of table names indicating each measurement parameter
    db_parameterIds = inspector.get_table_names()
    
    # Prepare a list of last time stamps extracted
    last_time_db = [[] for _ in db_parameterIds]
    
    params_stationId = {pid: [] for pid in parameterIds}
    
    for i in range(len(db_parameterIds)): # Loop over measurement parameters
        
        # Find the measurement station coordinates
        try: 
            db_locations = pd.read_sql(f'SELECT DISTINCT location_longitude, location_latitude FROM {db_parameterIds[i]}', engine)
        
        except (SQLAlchemyError, pd.errors.DatabaseError):
            
            print(f"No locations were found for the measurent parameter '{db_parameterIds[i]}'.")
            db_locations = []
        
        for j in range(len(db_locations)): # Loop over locations
            
            # Find the measurement station coordinates
            db_location = db_locations['location_longitude'][j], db_locations['location_latitude'][j]
            
            # If the last time stamp is later than the start time
            if start_time < pd.read_sql(f"SELECT * FROM {db_parameterIds[i]} WHERE location_longitude={db_location[0]} AND location_latitude={db_location[1]} ORDER BY time_to DESC", engine).loc[0].tolist()[0]: 
                
                # Add the station as trusted for this measurement parameter
                stationId = stations.loc[(stations.longitude == str(db_location[0])) & (stations.latitude == str(db_location[1])), 'stationId'].drop_duplicates().tolist()[0]
                params_stationId[db_parameterIds[i]].append(stationId) 
                
        # Find the last time stamp extracted
        try: 
            last_time_db[i] = pd.read_sql(f"SELECT time_to FROM {db_parameterIds[i]} ORDER BY time_to DESC LIMIT 1", engine).loc[0].tolist()[0]
        
        except (SQLAlchemyError, pd.errors.DatabaseError):
            
            print(f"No time stamps were found for the measurent parameter '{db_parameterIds[i]}'.")
            last_time_db[i] = 'NaT'
    
    # Convert last time stamp to ISO 8601
    times = pd.to_datetime(last_time_db)
    last_time_db = times.max().isoformat()
    
    if last_time_db=='NaT': 
        
        last_time_db = start_time
    
    return last_time_db, params_stationId

