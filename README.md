# Weather House

**Building and running a data warehouse with DMI climate data for planning outdoor projects.**

<img width="542" height="400" alt="image" src="https://github.com/user-attachments/assets/85bfae6c-a76d-40e9-a3ed-289fa285d7e3" />

https://www.dmi.dk/nyheder/2023/vejrstationer-i-verdenstop

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

The project uses a cloud data warehouse with agile analysis of weather conditions for outdoor projects at any location in Denmark, any time of the year and hour of the day.  
To achieve this goal, the classical extract, transform, load (ETL) scheme is changed to an extract, load, transform (ELT) scheme. 

<img width="672" height="384" alt="image" src="https://github.com/user-attachments/assets/ef1257ab-8609-4983-9366-7a080cfaaaf5" />

https://blog.devgenius.io/data-transformation-in-etl-process-d8efc8cf5338

## Modules and functions in the data warehouse

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

8. API server - Create an API server with FastAPI and SQLModel: 
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

# Mini app showcase on API
street_address = 'Kannikegade 18'
# street_address = 'Lautruphøj 1-3 A, Ballerup'
# street_address = 'Dannebrogsgade 2, Odense'
weather_app(street_address, stations, engine)



# Stop the API server
server.should_exit = True   # ask uvicorn to stop gracefully
thread.join()               # wait until it has finished
```

9. Close the PostgreSQL database engine
```python
# Close the PostgreSQL database engine
engine.dispose()
```

### Installing

* How/where to download your program
* Any modifications needed to be made to files/folders

### Executing program

* How to run the program
* Step-by-step bullets
```
code blocks for commands
```

## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Contributors names and contact info

ex. Dominique Pizzie  
ex. [@DomPizzie](https://twitter.com/dompizzie)

## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)
