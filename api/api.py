

# Import required libraries
from sqlalchemy import inspect
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, select


def api_server(engine): 
    
    # X 1. Setup for each measurement parameter and location in dmi_etl
    
    # --> 2. Setup for each measurement parameter and location in dmi_weathernorms
    
    '''
        API server
        
        Create an API server with  FastAPI and SQLModel: https://sqlmodel.tiangolo.com/
        
        
        Syntax: 
            
            api_server(engine)
        
        Query data from the API using the syntax: 
            
            http://127.0.0.1:8000/measurements/<parameter>
            
            <parameter> is the measurement parameter, e.g., mean_temp
            
            or: 
            
            http://127.0.0.1:8000/measurements/<parameter>?location_longitude=<location_longitude>&location_latitude=<location_latitude>
            
            <location_longitude> is the location longitude
            <location_latitude>  is the location latitude
            
            Example query: 
            
            http://127.0.0.1:8000/measurements/mean_temp?location_longitude=15.0953&location_latitude=55.0557
                
    '''
    
    # Create the class MeasurementBase with fields shared between the PostgreSQL database and the API
    class MeasurementBase(SQLModel): # (inherit from the class SQLModel)
    
        location_longitude: float              # Location longitude attribute
        location_latitude: float               # Location latitude attribute
        time_to: str = Field(primary_key=True) # Time stamp attribute
    
    # Create an inspector object
    inspector = inspect(engine)
    
    # Get a list of table names indicating each measurement parameter
    db_parameterIds = inspector.get_table_names()
    
    # Create data models
    models = {}
    for param_id in db_parameterIds:
        cls_name = "".join(part.capitalize() for part in param_id.split("_"))  # mean_temp -> MeanTemp
    
        models[param_id] = type(MeasurementBase)(
            cls_name,
            (MeasurementBase,),
            {
                "__annotations__": {param_id: float | None},
                param_id: None,
                "__tablename__": param_id,
                "__table_args__": {"extend_existing": True},
            },
            table=True,
        )
    
    # Dependency that opens a database session for each request
    # and closes it automatically when the request is finished.
    def get_session():
        
        with Session(engine) as session:
            
            yield session # Hand the session to the endpoint that asked for it
    
    # Shortcut type: "give me a Session, provided by get_session".
    # Endpoints can use SessionDep instead of repeating Annotated[...] every time.
    SessionDep = Annotated[Session, Depends(get_session)]
    
    # Create the FastAPI application
    app = FastAPI()
    
    @app.get("/measurements/{parameter}")
    def read_measurements(
        parameter: str,
        session: SessionDep,
        location_longitude: float | None = None,
        location_latitude: float | None = None,
        limit: int = 100,
    ):
        
        model = models.get(parameter)
        
        if model is None:
            
            raise HTTPException(404, f"Unknown parameter '{parameter}'")
        
        stmt = select(model)
        
        if location_longitude is not None:
            
            stmt = stmt.where(model.location_longitude == location_longitude)
        
        if location_latitude is not None:
            
            stmt = stmt.where(model.location_latitude == location_latitude)
    
        return session.exec(stmt.limit(limit)).all()
    
    
    return app

