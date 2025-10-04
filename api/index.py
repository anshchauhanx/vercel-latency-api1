from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

# Make POST requests from any origin allowed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"]
)

# Load the telemetry data ONCE at startup
with open("q-vercel-latency.json") as f:
    data = json.load(f)

@app.post("/")
async def check_latency(request: Request):
    payload = await request.json()
    regions = payload["regions"]
    threshold = payload["threshold_ms"]
    results = {}
    for region in regions:
        region_records = [rec for rec in data if rec["region"] == region]
        if not region_records:
            continue
        latencies = [rec["latency_ms"] for rec in region_records]
        uptimes = [rec["uptime_pct"] for rec in region_records]
        # Calculate mean latency/uptime
        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = sum(l > threshold for l in latencies)
        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }
    return results
