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



# Check whether the loaded data can be read into a pandas dataframe
# df = pd.read_sql(f"SELECT * FROM {parameterIds[0]}", engine)


# ---- ALTERNATIVE CODE ---

# import psycopg

# # Connect to an existing database
# conn = psycopg.connect(host="localhost",
#     port=5432,
#     dbname="dmi_etl",
#     user="nth",
#     password="pass",)

# # Open a cursor to perform database operations
# cur = conn.cursor()

# # Execute a command: this creates a new table
# cur.execute("""
#     CREATE TABLE test (
#         id serial PRIMARY KEY,
#         num integer,
#         data text)
#     """)



# # Pass data to fill a query placeholders and let Psycopg perform
# # the correct conversion (no SQL injections!)
# cur.execute(
#     "INSERT INTO test (num, data) VALUES (%s, %s)",
#     (100, "abc'def"))

# # Query the database and obtain data as Python objects.
# cur.execute("SELECT * FROM test")
# print(cur.fetchone())
# # will print (1, 100, "abc'def")

# # You can use `cur.executemany()` to perform an operation in batch
# cur.executemany(
#     "INSERT INTO test (num) values (%s)",
#     [(33,), (66,), (99,)])

# # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
# # of several records, or even iterate on the cursor
# cur.execute("SELECT id, num FROM test order by num")
# for record in cur:
#     print(record)

# Make the changes to the database persistent
# conn.commit()
        

# # %% Templates
# cur.execute(t"SELECT * FROM mytable WHERE id = {id}")
# cur.execute(
#     t"INSERT INTO mytable (first_name, last_name) VALUES ({first_name}, {last_name})"
# )

# # %% JSON adaptation
# from psycopg.types.json import Jsonb

# thing = {"foo": ["bar", 42]}
# conn.execute("INSERT INTO mytable VALUES (%s)", [Jsonb(thing)])


