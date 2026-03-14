"""
DriveSafe AI Service — main.py
FastAPI wrapper peste ADK Pipeline — Persoana 2
Rulează pe portul 8001 (separat de Backend pe 8000)
"""
import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from drivesafe_agent.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

app = FastAPI(title="DriveSafe AI Service", version="0.1.0")

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="drivesafe", session_service=session_service)


class AnalyzeTripRequest(BaseModel):
    trip_id: str
    user_id: str
    start_time: str
    end_time: str
    distance_km: float
    sensor_windows: list[dict]
    gps_polyline: list[dict]


@app.get("/health")
async def health():
    return {"status": "ok", "service": "drivesafe-ai"}


@app.post("/analyze")
async def analyze_trip(body: AnalyzeTripRequest):
    """
    Primește datele cursei de la Backend și rulează ADK Pipeline.
    Rezultatul se scrie direct în Firestore (prin TripSummaryAgent).
    """
    session = await session_service.create_session(
        app_name="drivesafe",
        user_id=body.user_id,
    )

    # Construiește mesajul de input pentru pipeline
    message = f"""
    Analyze this driving trip and generate a complete risk report:
    - Trip ID: {body.trip_id}
    - User ID: {body.user_id}
    - Duration: {body.start_time} to {body.end_time}
    - Distance: {body.distance_km} km
    - Sensor windows: {len(body.sensor_windows)} recorded events
    - Sensor data: {body.sensor_windows}
    - GPS polyline points: {len(body.gps_polyline)}

    Process all sensor windows, detect dangerous behaviors,
    calculate risk scores with road context, and save to Firestore.
    Generate a coaching report in Romanian.
    """

    content = types.Content(role="user", parts=[types.Part(text=message)])

    final_response = ""
    async for event in runner.run_async(
        user_id=body.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.is_final_response():
            final_response = event.content.parts[0].text

    return {"trip_id": body.trip_id, "status": "done", "summary": final_response}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8001)), reload=True)
