# Weather House

**Building and running a data warehouse with DMI climate data for planning outdoor projects.**

<img width="542" height="400" alt="image" src="https://github.com/user-attachments/assets/85bfae6c-a76d-40e9-a3ed-289fa285d7e3" />

( https://www.dmi.dk/nyheder/2023/vejrstationer-i-verdenstop )

The project uses a cloud data warehouse with agile analysis of weather conditions for outdoor projects at any location in Denmark, any time of the year and hour of the day.  

To achieve this goal, the classical extract, transform, load (ETL) scheme is changed to an extract, load, transform (ELT) scheme. 

<img width="672" height="384" alt="image" src="https://github.com/user-attachments/assets/ef1257ab-8609-4983-9366-7a080cfaaaf5" />

( https://blog.devgenius.io/data-transformation-in-etl-process-d8efc8cf5338 )

The data is loaded to a PostgreSQL database on [Docker](). 



### Dependencies

To run the data warehouse, the following Python libraries needs to be installed: 

[bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

[fastapi](https://fastapi.tiangolo.com/)

[geopy](https://geopy.readthedocs.io/en/stable/)

[numpy](https://numpy.org/install/)

[pandas](https://pandas.pydata.org/)

[plotly](https://plotly.com/python/getting-started/)

[requests](https://pypi.org/project/requests/)

[sqlalchemy](https://docs.sqlalchemy.org/en/21/intro.html#installation)

[sqlmodel](https://sqlmodel.tiangolo.com/#installation)

[uvicorn](https://uvicorn.dev/)



## Getting Started

Use the DMI ETL main routine launcher: 

```python
python -m dmi_etl
```

## Modules and functions in the data warehouse

<img width="1876" height="802" alt="image" src="https://github.com/user-attachments/assets/c38754e9-a620-4395-923e-6fd0a471a5d3" />


1. Connect to a database with user interface: 

```python
# Connect to the PostgreSQL database
# (NB: Remember to start the server on Docker)
# ( https://docs.sqlalchemy.org/en/21/intro.html )
location = 'localhost:5432'
dbname   = 'dmi_etl'
engine = condb.condb_ui(location, dbname)
```

2. Mini web scraper for extracting information about stations from DMI's online table: 

```python
# Find available stations
URL = "https://www.dmi.dk/friedata/dokumentation/data/climate-data-stations"
stations = extract.stations_scraper(URL)
```

3. Find the last time stamp extracted in the database and valid for each measurement parameter:
```python
# Find the last time stamp extracted in the database
last_time_db, params_stationId = condb.last_time_db(engine, start_time, stations, parameterIds)    
```

4. Extraction function for Climate Data API:
```python
# Extract new data from the DMI API
dat = extract.dmi_api_get(baseurl, stations, parameterIds, unit_mapping, start_time, last_time_db, params_stationId)
```

5. Find the last time stamp extracted from the API:
```python
# Find the last time stamp extracted from the API
last_time_api = extract.last_time_api(dat)
```

6. Load extracted data into database:
```python
# Load the new data into the PostgreSQL database
load.to_db(engine, parameterIds, dat)
```

7. Transform the data - Calculate averages, minimum and maximum for every hour in the days of a year, for every whether station, for every measurement parameter, and load the averages to new tables in the database:
```python
# Transform the data and upload the result to stats_{parameter_Id} tables
transform.transform(engine)
```

8. API server with mini app: 
```python
# Create an API server with FastAPI and SQLModel
app = api.api_server(engine)
# Create an API server with FastAPI and SQLModel
app = api.api_server(engine)

# Start the API server
config = uvicorn.Config(app, host="127.0.0.1", port=8000)
server = uvicorn.Server(config)
thread = threading.Thread(target=server.run, daemon=True)
thread.start()

# Mini app on the API
street_address = 'Kannikegade 18'
# street_address = 'Lautruphøj 1-3 A, Ballerup'
# street_address = 'Dannebrogsgade 2, Odense'
weather_app(street_address, stations, engine)

# Stop the API server
server.should_exit = True   # ask uvicorn to stop gracefully
thread.join()               # wait until it has finished
```

[![Temperature normals](https://github.com/user-attachments/assets/b0ea9428-413f-4f81-8c38-da486c9ab517)](https://raw.githack.com/nielsthaumann/dmi_etl/main/weather_app/temperature_normals.html)

9. Close the PostgreSQL database engine
```python
# Close the PostgreSQL database engine
engine.dispose()
```

### Installing

--- WILL BE ADDED LATER ---

* How/where to download your program
* Any modifications needed to be made to files/folders


# Unit tests
```python
'''
    Unit tests for DMI ETL
'''

# Connect a the PostgreSQL database
"""Verifying that NonExistingLocation exception is raised."""

# Mini web scraper for extracting information about stations from DMI's online table
"""Verifying that disabled internet connection is handled."""
"""Verifying that failure to read DMI's online table is stated."""

# Find the last time stamp extracted in the database and valid for each measurement parameter
"""Ensuring a datetime class as output from condb.last_time_db."""
"""Ensuring a dictionary with the parameterIds as keys as output from condb.last_time_db."""

# Extraction function for Climate Data API
"""Ensuring to get a list of pandas dataframes as output from extract.dmi_api_get."""

# Find the last time stamp extracted from the API
"""Ensuring a datetime class as output from extract.last_time_api."""

# Load extracted data into database
"""Ensuring that mock Loading of extracted data into database works."""

# Transform the data
"""Ensuring that transform.transform runs without error."""

```

<img width="660" height="500" alt="image" src="https://github.com/user-attachments/assets/730a5d90-5a18-4423-8e1b-3e60fdb43ce9" />
