'''
    Transform data
'''

import pandas as pd
from sqlalchemy import create_engine, inspect

def transform(engine): 
    '''
        
        
        Calculate averages, minimum and maximum 
        for every hour in the days of a year, 
        for every whether station, 
        for every measurement parameter, 
        and load the averages to new tables in the database. 
        
    '''
    
    # Create an inspector object
    inspector = inspect(engine)
    
    # Get a list of table names indicating each measurement parameter
    db_parameterIds = inspector.get_table_names()
    
    for i in range(len(db_parameterIds)): # Loop over measurement parameters
        
        # Calculate the average using SQL
        avg = pd.read_sql(f"SELECT location_longitude, location_latitude, SUBSTRING(time_to, 5) AS month_day_hour, AVG({db_parameterIds[i]}) AS avg_{db_parameterIds[i]} FROM {db_parameterIds[i]} GROUP BY location_longitude, location_latitude, SUBSTRING(time_to, 5) ORDER BY SUBSTRING(time_to, 5)", engine)
        avg['month_day_hour'] = pd.to_datetime(avg['month_day_hour'], utc=True, errors="coerce")
        
        # Find the measurement station coordinates
        db_locations = pd.read_sql(f'SELECT DISTINCT location_longitude, location_latitude FROM {db_parameterIds[i]}', engine)
        
        for j in range(len(db_locations)): # Loop over locations
            
            db_location = db_locations['location_longitude'][j], db_locations['location_latitude'][j]
            
            # Check with plotly
            import plotly.express as px
            import plotly.io as pio
            pio.renderers.default = 'browser'
            locids = ( avg.location_longitude==db_location[0] ) & ( avg.location_latitude==db_location[1] )
            fig = px.line(avg.loc[locids, ['month_day_hour', f'avg_{db_parameterIds[i]}']], x='month_day_hour', y=f'avg_{db_parameterIds[i]}')
            fig.update_traces(marker=dict(size=3))
            
    return

