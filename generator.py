import random
from datetime import datetime
import time
import json
import argparse




ANOMALY_CHANCE = 0.02
ANOMALY_MULTIPLIER = 1.5
#correctly formatting and producing the values based on the sensor configuration 
def make_reading(tick, sensor, baseline, noise, unit, drift_rate):
    value = random.gauss(baseline + tick * drift_rate, noise)
    if (random.random()<ANOMALY_CHANCE):
        value = value *ANOMALY_MULTIPLIER
    return{
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "sensor": sensor,
        "value": round(value, 1),
        "unit": unit,
    }

#sensor configuration including chamber pressure, fuel flow rate and chamber temperature
SENSORS = [
    {"sensor": "chamber_pressure", "baseline": 500, "noise": 5, "unit": "psi", "drift_rate": 0.05},
    {"sensor": "fuel_flow_rate", "baseline": 30, "noise": 1, "unit": "kg/sec", "drift_rate": 0.002},
    {"sensor": "chamber_temperature", "baseline": 1200, "noise": 20, "unit": "celsius", "drift_rate": 0.05}
]



def main(max_ticks):
    #prints the sensors every second
    tick = 0
    try:
        while tick<max_ticks:
            tick+=1
            for config in SENSORS:
                reading = json.dumps(make_reading(tick, **config))
                
                print(reading, flush=True) #flush = true allows the program to immediately write output instead of waiting in a memory buffer
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopped")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=int, default=float('inf'))
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    random.seed(args.seed)
    main(args.seconds)



