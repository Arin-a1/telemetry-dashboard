import sys
import json
import requests

API_URL = "http://127.0.0.1:8000/readings" #address of our post endpoint

for line in sys.stdin:
    try:
        reading = json.loads(line) # load s (s stands for string)- this loads json from a string. opposite of json.dumps()
    except json.decoder.JSONDecodeError: #this is dealing with the cases where we run into "Stopped" or ""
        continue
    response = requests.post(API_URL, json = reading) #sends a POST request with a JSON body. 
    print(response.status_code)
    

#python generator.py --seconds 3 | python ingest.py
# | is a pipe and it takes the ouput of generator.py --seconds 3 and puts it as input into ingest.py
# i think strip() removes the unnecessary whitespace?
# flush = true matters because it allows us to see each of the three lines in real time instead of having to wait for all of them to arrive