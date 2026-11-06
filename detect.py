from collections import deque
import requests
from detector import is_anomaly
from statistics import mean

API_URL = "http://127.0.0.1:8000/readings" #address of our get endpoint
WINDOW = 30

def check_sensor(sensor):
    response = requests.get(API_URL, params={"sensor": sensor, "limit": 500})
    readings = response.json()
    readings.reverse() #the api returns the newest first so we have to flip it so we can walk forwards

    history = deque(maxlen=WINDOW) #list with a size cap of WINDOW. once it holds WINDOW number of items, it silently drops the oldest to make space

    flagged = 0
    streak = 0
    for r in readings:
        if is_anomaly(history, r["value"]):
            flagged += 1
            streak += 1
            if streak >= 5:
                print("ANOMALY", r["timestamp"], sensor, r["value"], f"window mean {mean(history):.1f}")
                history.clear()
                print("RESET", r["timestamp"], sensor)
                history.append(r["value"])
                streak = 0
            else:
                print("ANOMALY", r["timestamp"], sensor, r["value"], f"window mean {mean(history):.1f}")
        else:
            history.append(r["value"])
            streak = 0
        
    print(f"{sensor}: {len(readings)} readings, {flagged} flagged")


for sensor in ["chamber_pressure", "fuel_flow_rate", "chamber_temperature"]:
    check_sensor(sensor)
