'''
    Connect to PostgreSQL database
'''

# Import required libraries
from sqlalchemy import database_exists, create_database, create_engine


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

