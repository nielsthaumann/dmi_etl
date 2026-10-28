# Weather House

**Building and running a data warehouse with DMI climate data for planning outdoor projects.**

<img width="450" height="332" alt="image" src="https://github.com/user-attachments/assets/85bfae6c-a76d-40e9-a3ed-289fa285d7e3" />

https://www.dmi.dk/nyheder/2023/vejrstationer-i-verdenstop

### Dependencies

The data warehouse needs the following Python libraries installed to run: 

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


1. Creating and connecting a PostgreSQL database on Docker. 

```python
location = 'localhost:5432'
dbname   = 'dmi_etl'
engine = condb.condb_ui(location, dbname)
```

2. ....

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
