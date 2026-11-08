from collections import deque
import requests
from detector import is_anomaly
import time

API_URL = "http://127.0.0.1:8000/readings" #address of our get endpoint for list of readings
ANOMALY_URL = "http://127.0.0.1:8000/anomalies" # address of our post endpoint for list of anomalies
WINDOW = 30
SENSORS = ["chamber_pressure", "fuel_flow_rate", "chamber_temperature"]
#checking if a sensor if an anomaly or not based on the values of the sensors that came before it (history)
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
            print("ANOMALY", r["timestamp"], sensor, r["value"])
            if streak >= 5:
                history.clear()
                print("RESET", r["timestamp"], sensor)
                history.append(r["value"])
                streak = 0

            response = requests.post(ANOMALY_URL, json={
                "reading_id": r["id"],
                "timestamp": r["timestamp"],
                "sensor": sensor,
                "value": r["value"]
            })
            response.raise_for_status()
        else:
            history.append(r["value"])
            streak = 0
        
    print(f"{sensor}: {len(readings)} readings, {flagged} flagged")


def run_once():
    for sensor in SENSORS:
        check_sensor(sensor)


if __name__ == "__main__":
    try:
        while True:
            try:
                run_once()
            except requests.exceptions.RequestException:
                print("API unreachable, retrying ...")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopped")
