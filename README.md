# Weather House

<img width="500" alt="image" src="https://github.com/user-attachments/assets/85bfae6c-a76d-40e9-a3ed-289fa285d7e3" />

[(*Weather station in Tasiilaq on the east coast of Greenland)*]( https://www.dmi.dk/nyheder/2023/vejrstationer-i-verdenstop )

## What is a cloud data warehouse?

The "cloud data warehouse" is not a literal floating cloud of information stored in a house in the sky but a shared server (computer) environment where selected data can be stored and processed online.

[Dansk Industri](https://www.danskindustri.dk/vi-radgiver-dig/forretningsudvikling/digitalisering-og-innovation/grib-nye-teknologier/cloud/) denounces cloud solutions as the next genereation IT and lists a set of advantages of the cloud computing over traditional IT: 

**The Benefits of Cloud Computing**
- *Cloud computing offers greater flexibility, allowing your business to **respond more quickly to changing needs and requirements**.*
- *Cloud solutions allow employees to access documents and systems from anywhere with an internet connection, **making hybrid working easier**.*
- *You **avoid the need for major hardware investments**, which are typically required with traditional IT solutions.*
- *Software **maintenance and updates are easier**, saving the IT department valuable time.*
- *Cloud solutions **can easily be scaled up or down** to match your needs. Many cloud services are subscription-based, which can also offer financial benefits.*
- ***Data recovery is less costly** in the event of data loss or system failure.*

## Building and running a cloud data warehouse with DMI climate data for planning outdoor projects

The current project builds and operates a cloud data warehouse, enabling agile analysis of weather conditions for outdoor projects across Denmark, at any time of the year or day.

To achieve this goal, the classical extract, transform, load (ETL) scheme is changed to an extract, load, transform (ELT) scheme. 

<img
  width="700"
  alt="Animated demo"
  src="https://miro.medium.com/v2/resize:fit:1100/1*c77MbjfOCxijKIOZ0z3KFw.gif"
/>

[*(Difference between ETL and ELT)*](https://blog.devgenius.io/data-transformation-in-etl-process-d8efc8cf5338)

The data is loaded to a [PostgreSQL](https://hub.docker.com/_/postgres) database on [Docker](https://hub.docker.com/_/postgres). 

Finally, for secure data usage, the data is accessed with user restrictions via an application programming interface (API) server. 

### Dependencies

To run the data warehouse, the following Python libraries and applications needs to be installed: 

<br>

#### Extract

<a href="https://medium.com/@pratik_shrestha/exploring-web-scraping-with-beautiful-soup-in-python-6d7408e3bfd1">
  <img src="https://github.com/user-attachments/assets/1c7b635d-ad61-4e21-b257-0750212a2d46" height="100" alt="Beautiful Soup">
</a>

https://github.com/user-attachments/assets/a4bb2fd6-5011-4020-a5f6-d6a695d0340f


<br>
<a href="https://pypi.org/project/requests">
  <img src="https://github.com/user-attachments/assets/a4bb2fd6-5011-4020-a5f6-d6a695d0340f" height="200" alt="requests">
</a>

<br>

#### Load

<br>
<a href="https://www.docker.com/products/docker-desktop">
  <img src="https://github.com/user-attachments/assets/bcade83d-6bf2-40dd-b280-5f218f5a69f9" height="200" alt="docker">
</a>


<br>
<a href="https://pandas.pydata.org">
  <img src="https://github.com/user-attachments/assets/7f50f67f-bd6e-4609-9cf7-a3ca90b3adfa" height="100" alt="pandas">
</a>

<br>
<a href="https://docs.sqlalchemy.org/en/21/intro.html#installation">
  <img src="https://github.com/user-attachments/assets/a40e55d5-f720-46c7-86c4-03937aad5513" height="100" alt="sqlalchemy">
</a>

<br>

#### Transform

<br>
<a href="https://numpy.org/install">
  <img src="https://github.com/user-attachments/assets/79c2a786-7b3f-41ec-a4d5-38f85db11ae5" height="100" alt="numpy">
</a>

<br>
<a href="https://fastapi.tiangolo.com">
  <img src="https://github.com/user-attachments/assets/a5717c33-087d-42db-8734-1642a9a4bc76" height="100" alt="Fast API">
</a>

<br>
<a href="https://geopy.readthedocs.io/en/stable">
  <img src="https://github.com/user-attachments/assets/8c160a7c-e1e4-441c-b0a0-205adc980e6a" height="100" alt="geopy">
</a>

<br>
<a href="https://plotly.com/python/getting-started">
  <img src="https://github.com/user-attachments/assets/7f1915ca-da37-4a61-83dd-99528a592381" height="100" alt="plotly">
</a>

<br>
<a href="https://sqlmodel.tiangolo.com/#installation">
  <img src="https://github.com/user-attachments/assets/b7efce32-195c-4cdc-bfe9-636676115984" height="100" alt="sqlmodel">
</a>

<br>
<a href="https://uvicorn.dev">
  <img src="https://github.com/user-attachments/assets/ad0a6bd9-b52f-46d0-9bb1-724f8b608b95" height="300" alt="uvicorn">
</a>

<br>

## Getting Started

Use the DMI ETL main routine launcher: 

```python
python -m dmi_etl
```

## Modules and functions in the data warehouse

<img width="1280" height="592" alt="Modules and functions in the data warehouse" src="https://github.com/user-attachments/assets/03a84492-56f7-415f-8820-cfe63393f1f9" />

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

7. Transform the data - Calculate averages, minimum and maximum for every hour in the days of a year, for every weather station, for every measurement parameter, and load the averages to new tables in the database:
```python
# Transform the data and upload the result to stats_{parameter_Id} tables
transform.transform(engine)
```

8. API server with mini app: 
```python
# Create an API server with FastAPI, SQLModel, and Uvicorn
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
*(Click on the plot above to interact with the data and explore different visualizations*)

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
