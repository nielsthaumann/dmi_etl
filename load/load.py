'''
    Load data into database
'''


def to_db(engine, parameterIds, dat): 
    '''
        load.to_db(engine, parameterIds, dat)
        
        Load extracted data into database
    '''
    
    # Write to the database
    # ( https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html )
    
    for i in range(len(dat)): # Loop over measurement parameters
        
        if not dat[i].empty: 
            
            print(f'\nLoading {parameterIds[i]} data into database...', end='')
            
            dat[i].to_sql(parameterIds[i], engine, if_exists='append', index=False)
            
            print('completed. ✅')
        
        else:
            
            print(f'\nSkipping empty dataframe for {parameterIds[i]}. 🟡')


