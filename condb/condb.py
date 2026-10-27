'''
    Connect to PostgreSQL database
'''

# Import required libraries
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine, inspect
from sqlalchemy import text
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from tkinter import simpledialog, messagebox
import socket
import traceback


class NonExistingLocation(Exception):
    def __init__(self, location):
        self.location = location
        super().__init__(f"\n\nFailed connecting to location '{location}'. \nPlease ensure that the location is correct and the database server is online. ")

class FailedDbConnection(Exception):
    def __init__(self, location):
        self.location = location
        super().__init__(f"\n\nFailed connecting to location '{location}'. \nPlease ensure that the location is correct and the database server is online. ")



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
        
        raise NonExistingLocation(location)
        
    
    # User interface for connecting to database
    # (Note there is a smaller risk: If the users' machine is infected by mallicious software, 
    # the password temporarilly transferred unencrypted in RAM might be picked up by a hacker. 
    # On the server side, there is also a smaller risk: The password may be stored in files on the server as unencrypted text.
    # Also, the connection to the database is not protected with SSL on the internal network on the server side.) 
    def condb_prompt(): 
        
        username = simpledialog.askstring(title="User name", prompt='Please enter a valid user name:')
        password = simpledialog.askstring(title="Password", prompt='Please enter a valid password:', show="*") # Mask display with *
        
        return username, password
    
    username, password = condb_prompt()
    
    url = 'postgresql+psycopg://' + username + ':' + password + '@' + location + '/'+ dbname
    
    try: 
        
        # Check if database already exists or needs to be created
        if not database_exists(url):
            
            print(f"Cannot access the database '{dbname}'. Attempting to create the database and reconnect. ")
            create_database(url)
        
        # Connect to the database
        engine = create_engine(url)
        
        # Check if the security setting are invalid
        if not database_exists(url):
            
            raise FailedDbConnection(location)
    
        return engine    
    
    except Exception as e:
        
        if 'connection failed' in str(e): 
            
            raise FailedDbConnection


def condb_ui(location, dbname): 
    
    '''
    Connect to a database with user interface
    
    Syntax: 
        
        engine = condb_ui(location, dbname)
        
    '''
    
    while True: 
        
        try: 
            
            engine = condb(location, dbname)
            
            return engine
        
        except Exception as e:
            
            if 'password authentication failed' in str(e): 
                
                if messagebox.askyesno(title="Wrong user name or password", 
                                       message='The user name or password was wrong. \nDo you want to try again'): 
                
                    continue
                
                else: 
                    
                    raise SystemExit("Login cancelled")
        
            else:
                
                traceback.print_exc() # Show exception traceback
                return
                


def last_time_db(engine, start_time, stations, parameterIds): 
    '''
        
    Find the last time stamp extracted in the database and valid for each measurement parameter
    
    Syntax: 
        
        last_time_db, params_stationId = condb.last_time_db(engine, start_time, stations, parameterIds)
        
    '''
    
    # Create an inspector object
    inspector = inspect(engine)
    
    # Get a list of table names indicating each measurement parameter
    db_parameterIds = [
        t for t in inspector.get_table_names()
        if {'location_longitude', 'location_latitude', 'time_to'}
           <= {c['name'] for c in inspector.get_columns(t)}
    ]
    
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
        
        
        # Query valid locations for the measurement parameter, use conversion of numers to text and rename to match station table columns
        query = text(f"""
            SELECT location_longitude::text AS longitude, location_latitude::text AS latitude
            FROM {db_parameterIds[i]}
            GROUP BY location_longitude, location_latitude
            HAVING MAX(time_to) > :start_time
        """)
        valid_locations = pd.read_sql(query, engine, params={"start_time": start_time})
        
        ids = valid_locations.merge(stations, on=['longitude', 'latitude'])['stationId'].drop_duplicates()
        params_stationId[db_parameterIds[i]].extend(ids.tolist())
        
        
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

