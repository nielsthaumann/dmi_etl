'''
    API
'''

# https://www.geeksforgeeks.org/python/fastapi-sqlite-databases/

# Import required libraries
from condb import condb
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, select
import subprocess



# Connect to the PostgreSQL database
# (NB: Remember to start the server on Docker)
# ( https://docs.sqlalchemy.org/en/21/intro.html )
# --- ADD USER PROMPT HERE ---
username = 'nth'
password = 'pass'
location = 'localhost:5432'
dbname   = 'dmi_etl'
# ---- # 
engine = condb.condb(username, password, location, dbname)


class TempBase(SQLModel):
    time_to: str = Field(primary_key=True)
    location_longitude: float
    location_latitude: float
    mean_temp: float | None = None


class Temp(TempBase, table=True):
    __tablename__ = "mean_temp"  # must match your existing table name


class TempPublic(TempBase):
    pass


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.get("/temps/", response_model=list[TempPublic])
def read_temps(
    session: SessionDep,
    name: str | None = None,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    statement = select(Temp)
    if name:
        statement = statement.where(Temp.name == name)
    return session.exec(statement.offset(offset).limit(limit)).all()


@app.get("/temps/{temp_id}", response_model=TempPublic)
def read_temp(temp_id: int, session: SessionDep):
    temp = session.get(Temp, temp_id)
    if not temp:
        raise HTTPException(status_code=404, detail="Temp not found")
    return temp



if __name__ == "__main__":
    
    p = subprocess.Popen('start "uvicorn" cmd /k python -m uvicorn api.api:app --port 8003', shell=True)




# --- ALTERNATIVE CODE ---
# 
# # Database setup
# engine = condb.condb(username, password, location, dbname)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = sqlalchemy.orm.declarative_base()

# # Define the Database Model
# class Item(Base):
#     __tablename__ = "items"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)
#     description = Column(String)

# # Create necessary tables in the database
# Base.metadata.create_all(bind=engine)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# class ItemCreate(BaseModel):
#     name: str
#     description: str

# class ItemResponse(BaseModel):
#     id: int
#     name: str
#     description: str
    
# @app.get("/items/{item_id}", response_model=ItemResponse)
# async def read_item(item_id: int, db: Session = Depends(get_db)):
#     db_item = db.query(Item).filter(Item.id == item_id).first()
#     if db_item is None:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return db_item

# --- ALTERNATIVE CODE ---

# parameterId='mean_temp'
# @app.get("/mean_temp")


# # Define a simple GET endpoint
# @app.get("/")
# def read_root():
#     return {"message": "Hello World"}

# @app.get("/niels")
# def read_root():
#     return {"message": "hej niels"}


# --- ALTERNATIVE CODE ---

# subprocess.Popen(f'start "uvicorn" cmd /k python -m uvicorn api:app', shell=True)

# p = subprocess.Popen([f"{sys.executable} -m uvicorn api:app --reload"], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

# uvicorn.run("api:app", reload=True)
