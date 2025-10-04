from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

with open("q-vercel-latency.json") as f:
    data = json.load(f)

@app.options("/api/latency")
async def preflight_handler():
    return JSONResponse(content={}, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    })

@app.post("/api/latency")
async def check_latency(request: Request):
    payload = await request.json()
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 0)
    results = {}
    for region in regions:
        region_records = [rec for rec in data if rec.get("region") == region]
        if not region_records:
            continue
        latencies = [rec.get("latency_ms") for rec in region_records]
        uptimes = [rec.get("uptime_pct") for rec in region_records]
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
