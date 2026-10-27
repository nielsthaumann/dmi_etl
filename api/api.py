

# Import required libraries
from sqlalchemy import inspect
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, select
from sqlalchemy import text

def api_server(engine): 
    
    
    '''
        API server
        
        Create an API server with  FastAPI and SQLModel: https://sqlmodel.tiangolo.com/
        
        
        Syntax: 
            
            api_server(engine)
        
        Query data from the API using the syntax: 
            
            http://127.0.0.1:8000/measurements/<parameter>
            
            <parameter> is the measurement parameter, e.g., stats_mean_temp
            
            or: 
            
            http://127.0.0.1:8000/measurements/<parameter>?location_longitude=<location_longitude>&location_latitude=<location_latitude>
            
            <location_longitude> is the location longitude
            <location_latitude>  is the location latitude
            
            Example query: 
            
            http://127.0.0.1:8000/measurements/stats_mean_temp?location_longitude=15.0953&location_latitude=55.0557
                
    '''
    
    # Create the class MeasurementBase with fields shared between the PostgreSQL database and the API
    class MeasurementBase(SQLModel): # (inherit from the class SQLModel)
    
        location_longitude: float              # Location longitude attribute
        location_latitude: float               # Location latitude attribute
        month_day_hour: str = Field(primary_key=True) # Time stamp attribute
    
    # Create an inspector object
    inspector = inspect(engine)
    
    # Get a list of table names indicating each measurement parameter starting with 'stats_'. 
    with engine.connect() as conn:
        db_parameterIds = [
            t for t in inspector.get_table_names()
            if t.startswith('stats_')
            and conn.execute(text(f'SELECT EXISTS (SELECT 1 FROM "{t}")')).scalar()
        ]
    
    # Create data models
    models = {}
    for param_id in db_parameterIds:
        
        cls_name = "".join(part.capitalize() for part in param_id.split("_"))
        
        name = param_id[6:]  # strip the 'stats_' prefix
        
        # Drop any stale definition so extend_existing can't merge old columns into the new class
        if param_id in SQLModel.metadata.tables:
            SQLModel.metadata.remove(SQLModel.metadata.tables[param_id])
        
        models[param_id] = type(MeasurementBase)(
            cls_name,
            (MeasurementBase,),
            {
                "__tablename__": param_id,
                "__annotations__": {
                    f"min_{name}": float | None,
                    f"avg_{name}": float | None,
                    f"max_{name}": float | None,
                },
                f"min_{name}": None,
                f"avg_{name}": None,
                f"max_{name}": None,
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
        limit: int = 200000,
    ):
        
        model = models.get(parameter)
        
        if model is None:
            
            raise HTTPException(404, f"Unknown measurement parameter '{parameter}'")
        
        stmt = select(model) # Define the statement for the request
        
        if location_longitude is not None: # Use longitude constraint
            
            stmt = stmt.where(model.location_longitude == location_longitude)
        
        if location_latitude is not None: # Use latitude constraint
            
            stmt = stmt.where(model.location_latitude == location_latitude)
    
        return session.exec(stmt.limit(limit)).all() # Execute session
    
    return app

