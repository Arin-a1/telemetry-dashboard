# Test stand telemetry

[One sentence: what this is, and that the data is simulated.]

![Dashboard](docs/dashboard.png)

## What it does
[3 short bullets: generates sensor data, stores and serves it over a REST API, shows it live and flags anomalies.]

## Architecture
```
generator.py --JSON lines--> ingest.py --POST /readings--> FastAPI + SQLite
detect.py --GET /readings, POST /anomalies--> FastAPI + SQLite
dashboard (HTML + Chart.js) --GET /readings, GET /anomalies--> FastAPI + SQLite
```

## Run it locally
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r requirements.txt`
3. In separate terminals:
   - `uvicorn api:app --reload`
   - `cd dashboard && python -m http.server 5500`
   - `python generator.py | python ingest.py`
   - `python detect.py`
4. Open http://localhost:5500

## How anomaly detection works
[Rolling window of 30 values, z-score threshold of 3, flagged values kept out of the window, reset after 5 in a row. Say why in a sentence each.]

## Limitations and next steps
[Be honest: detection runs in batches, the dashboard polls, SQLite allows one writer, no authentication. Say what you'd change.]