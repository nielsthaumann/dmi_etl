'''
    Transform data
'''

import pandas as pd
from sqlalchemy import inspect
from sqlalchemy import text

def transform(engine): 
    '''
        Transform the data
        
        Syntax: 
            
            transform(engine)
        
        Calculate averages, minimum and maximum 
        for every hour in the days of a year, 
        for every whether station, 
        for every measurement parameter, 
        and load the averages to new tables in the database. 
        
    '''
    
    # Create an inspector object
    inspector = inspect(engine)
    
    # Get a list of table names indicating each measurement parameter. 
    # NB: Exclude db_parameterIds with empty tables or starting with 'stats_'
    with engine.connect() as conn:
        db_parameterIds = [
            t for t in inspector.get_table_names()
            if not t.startswith('stats_')
            and conn.execute(text(f'SELECT EXISTS (SELECT 1 FROM "{t}")')).scalar()
        ]
    
    for i in range(len(db_parameterIds)): # Loop over measurement parameters
        
        # Calculate the minimum, average, and maximum measurement values across years using SQL
        print(f"\nCalculating the minimum, average, and maximum '{db_parameterIds[i]}' measurement values across years using SQL.")
        stats = pd.read_sql(f"SELECT location_longitude, location_latitude, SUBSTRING(time_to, 5) AS month_day_hour, MIN({db_parameterIds[i]}) AS min_{db_parameterIds[i]}, AVG({db_parameterIds[i]}) AS avg_{db_parameterIds[i]}, MAX({db_parameterIds[i]}) AS max_{db_parameterIds[i]} FROM {db_parameterIds[i]} GROUP BY location_longitude, location_latitude, SUBSTRING(time_to, 5) ORDER BY SUBSTRING(time_to, 5)", engine)
        stats['month_day_hour'] = pd.to_datetime(stats['month_day_hour'], utc=True, errors="coerce")
        
        # Load to database
        print(f"Loading the result to the descriptive statistics to the the table '{'stats_' + db_parameterIds[i]}'.")
        stats.to_sql('stats_' + db_parameterIds[i], engine, if_exists='replace', index=False)
        
    return

