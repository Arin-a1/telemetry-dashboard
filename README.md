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

Each sensor is judged separately against its own recent behavior, since the sensors live on very different scales (about 500 psi for pressure, about 30 kg/sec for fuel flow).

`detect.py` walks through a sensor's readings from oldest to newest. For each reading, `detector.py` computes a z-score: how many standard deviations the reading sits from the mean of the previous 30 readings. A reading is flagged when its z-score is above 3. Flags are stored in an `anomalies` table, keyed by the reading's id, and the dashboard highlights those points in red.

The parameters and the reasons for them:

- **Rolling window of 30 readings.** Long enough to give a stable mean and standard deviation, short enough to follow slow drift instead of treating it as a fault.
- **Threshold of 3 standard deviations.** For normally distributed noise, only about 0.3% of normal readings fall beyond it (a little more in practice, since the window's standard deviation is itself noisy). The injected faults sit far past it. A lower threshold would catch subtler faults at the cost of more false alarms.
- **Absolute value of the z-score.** A sudden drop is as suspicious as a spike.
- **Minimum history of 10 readings.** A mean and standard deviation from a handful of points aren't meaningful, so early readings are never judged. A window with zero variance is also skipped to avoid dividing by zero.
- **Flagged readings stay out of the window.** Otherwise one large spike inflates the standard deviation and can hide the next anomaly.
- **Reset after 5 flags in a row.** Five consecutive flags are not a spike, they mean the sensor's level has shifted. Without a reset, the window stays frozen at the old level and flags every reading that follows. In testing, a single level shift produced about 200 consecutive false flags before I added this. After a reset, the window restarts from the current reading.

Re-running detection is safe: the `reading_id` column is unique and inserts use `INSERT OR IGNORE`, so the same flag is never stored twice.

## Limitations and next steps

**Detection**

- **It runs in batches.** Every 5 seconds, `detect.py` re-fetches the newest 500 readings per sensor and re-judges them from scratch. Because that slice moves forward, borderline readings can flip between flagged and not flagged from one pass to the next, and since the `anomalies` table only accumulates, an earlier flag stays even if a later pass would not raise it. The better design is incremental: judge each reading once, as it arrives, using a rolling window kept per sensor.
- **Sustained faults get absorbed.** After a reset, a real, lasting fault becomes the new baseline, and there is a blind spot of about 10 readings while the new window refills. A production system would alert on sudden spikes and sustained shifts as separate conditions.
- **The method assumes roughly Gaussian noise.** The simulated data fits that. Real sensors often do not.
- **It hasn't been scored.** The generator does not record which readings it spiked, so I can't report precision and recall. A next step is to have the generator write an answer key and measure the detector against it.

**Architecture**

- **The dashboard polls.** It requests fresh data every 5 seconds, which is fine for one viewer but multiplies with many. WebSockets or server-sent events would push updates instead.
- **SQLite and one request per reading.** SQLite allows a single writer at a time, and the ingest script makes one HTTP request per reading. That's comfortable at about 3 readings per second. Scaling up would mean a batch endpoint and a database like Postgres or TimescaleDB.
- **No authentication.** The write endpoints are open to anyone who can reach the API. The CORS setting only restricts browsers, not other clients. Before deploying, I would add API keys on write endpoints and rate limiting.
- **Timestamps have no time zone.** They are stored as local-time strings, and the dashboard's "Live" indicator assumes it runs on the same machine. UTC timestamps with an offset would fix this.
- **The data is simulated.** The generator is a model of a test stand, not real telemetry.
- **Planned:** automated tests for the detector and API, and a CI workflow that runs them on every push.