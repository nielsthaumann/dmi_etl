'''
    Tranform data
'''

def dbinfo(engine): 
    '''
        
        
        Find time stamps, locations, and measurements in the database
    '''
    import pandas as pd
    timestamps = pd.read_sql('SELECT time_to FROM mean_temp', engine)
    
    # --- ADD HERE ---
    
    