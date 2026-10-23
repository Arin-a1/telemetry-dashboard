from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI() #this is creating the app and everything else that attached to it

#--reload flag restarts the server whenver i save a change to my code. without that you would have to stop and restart the server by hand before seeing your changes

DB_PATH= 'telemetry.db'

def get_connection(): #helper so we don't have to repeat over and over when opening the db file
    conn= sqlite3.connect(DB_PATH) #opening the database file, creating it if it doesn't exist. kind of like opening a file cabinet
    conn.row_factory = sqlite3.Row # this lets you read a row by column name. eg. row["sensor"], and importantly lets you convert it to a disctionary which fastapi can turn into json
    return conn

def init_db():
    conn= get_connection()
    conn.execute(""" 
        CREATE TABLE IF NOT EXISTS readings(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            timestamp TEXT NOT NULL,
            sensor TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL
        )
    """)
    conn.commit() #saving our changes
    conn.close() #closing the connection when you are done

init_db()

class Reading(BaseModel):
    timestamp: str
    sensor: str
    value: float
    unit: str

@app.get("/health") #when someone visits the endpoint /health, run the function right below me
def health(): # ordinary python function
    return {"status": "ok"} #fastAPI turns the dictionary into json automatically

@app.post("/readings", status_code=201) #when someone visits the endpoint /readings, execute the add_reading function. this is a post request so it is saying i am sending you data to save
#201 status code means created which is better than 200 which just means OK
def add_reading(reading: Reading): #if incoming data is not of object type Reading(doesn't match the shape), FastAPI reject it before the code even runs
    conn = get_connection() #opening the file cabinet once again
    conn.execute(
        "INSERT INTO readings (timestamp, sensor, value, unit) VALUES (?, ?, ?, ?)",
        (reading.timestamp, reading.sensor, reading.value, reading.unit),

    )
    conn.commit() #saving
    conn.close() #closing file cabinet
    return reading #returning what reading we just added

@app.get("/readings") #same endpoint as above except this is a different method (get)
def list_readings(sensor: str | None = None, start:str | None = None, end:str | None = None, limit:int = 100): #takes in sensor as a parameter that fastapi reals from the url (eg. /readings?sensor=chamber_pressure)
    #takes start and end timestamp and filters for readings within that time period
    query = "SELECT * FROM readings WHERE 1=1"
    params = []

    if sensor:
        query += " AND sensor = ?"
        params.append(sensor)
    if start:
        query += " AND timestamp >= ?"
        params.append(start)
    if end:
        query += " AND timestamp <= ?"
        params.append(end)
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

#questions
#why do we need to close our connections when we are donw in init_db. why can't we keep in open. is it kind of like closing the database file?
#in list_readings, what is the .fetchall() doing and why cant we just do the plain sql command
#why does execute want a tuple when we are trying to fill in placeholders?

# def list_readings(sensor: str | None = None, start:str | None = None): #takes in sensor as a parameter that fastapi reals from the url (eg. /readings?sensor=chamber_pressure)
#     conn = get_connection()
#     if sensor: #if there is a sensor that was provided
#         rows = conn.execute("SELECT * from readings WHERE sensor = ?", (sensor,)).fetchall() #give me every column from every row in the data table 
#         #sensor = (?) (sensor) filters for all the rows with that specific censor name
#         #(sensor,)- this is a tuple because execute wants a tuple
#         # .fetchall() pulls the matching row into python as a list
#         #using ? instead of an f-string prevents SQL injection where the database would treat everything like a real instruction as opposed to data
#         #eg if we had something like WHERE sensor = x or '1'='1', this would always evaluate to true and we would return the whole databse and a worse input could modify or delete the data
#         #but using ?, SQL will try to look for a sensor literally named x or '1'='1' and will find nothing 
#     else:
#         rows = conn.execute("SELECT * from readings").fetchall()
#     conn.close()
#     return [dict(row) for row in rows]