from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dashboard_data import load_dashboard

DATA = Path(__file__).parent / "data"

app = FastAPI(title="Email triage dashboard")

# Only the local dev front end may call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/emails")
def emails() -> dict:
    return load_dashboard(DATA)
