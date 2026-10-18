'''
    Load data into Docker PostgreSQL database
'''


# Import required libraries
import pandas as pd
# import psycopg
from sqlalchemy import create_engine

# Load the extracted data locally
parameterIds = ['mean_temp',          # Mean temperature °C
                'mean_relative_hum',  # Mean relative humidity %
                'mean_wind_speed',    # Mean wind speed m/s
                'bright_sunshine',    # Minutes/hours of bright sunshine
                'mean_radiation',     # Mean radiation (spectral range: 305-2800nm) W/m^2
                'mean_cloud_cover',   # Cloud cover %
                'acc_precip',         # Accumulated precipitation mm
                'snow_depth',         # Snow depth cm
                ]
dat = [[None]]*len(parameterIds) # Prepare a list of pandas dataframes with extracted data ( dat[parameter] )
for i, parameterId in enumerate(parameterIds): # Loop over parameters
    
    dat[i] = pd.read_pickle(f'dmi_api_{parameterIds[i]}.pkl')


# Connect to the database
engine = create_engine("postgresql+psycopg://nth:pass@localhost:5432/dmi_etl")

# Write to the database
# ( https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html )
for i, parameterId in enumerate(parameterIds): # Loop over parameters
    dat[i].to_sql(parameterIds[i], engine, if_exists="append", index=False)


# # Read from the database
# df = pd.read_sql(f"SELECT * FROM {parameterIds[0]}", engine)



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
conn.commit()
        

# # %% Templates
# cur.execute(t"SELECT * FROM mytable WHERE id = {id}")
# cur.execute(
#     t"INSERT INTO mytable (first_name, last_name) VALUES ({first_name}, {last_name})"
# )

# # %% JSON adaptation
# from psycopg.types.json import Jsonb

# thing = {"foo": ["bar", 42]}
# conn.execute("INSERT INTO mytable VALUES (%s)", [Jsonb(thing)])


