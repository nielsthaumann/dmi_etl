'''
    API
'''

# Import required libraries
from fastapi import FastAPI
import asyncpg

# Create FastAPI app instance
app = FastAPI()


# ---> Define GET syntax ---


# Define a simple GET endpoint
@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/niels")
def read_root():
    return {"message": "hej niels"}


# --- ALTERNATIVE CODE ---

# subprocess.run(["uvicorn", "api:app", "--reload"], check=True)

# uvicorn.run("api:app", reload=True)
