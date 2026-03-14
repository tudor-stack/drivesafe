"""
app/api/trips.py — Endpoints pentru curse
Persoana 1 implementează logica, Persoana 3 (mobile) consumă aceste endpoint-uri.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import httpx
import os

from app.core.auth import get_current_user
from app.services.firestore_service import FirestoreService

router = APIRouter()
firestore = FirestoreService()

class ProcessTripRequest(BaseModel):
    trip_id: str
    start_time: str
    end_time: str
    distance_km: float
    sensor_windows: list[dict]
    gps_polyline: list[dict]

# 1. Logica de AI în fundal (Fără timeout-uri care omoară aplicația)
async def send_to_ai_service(trip_id: str, payload: dict):
    ai_service_url = os.environ.get("AI_SERVICE_URL", "http://localhost:8001")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{ai_service_url}/analyze", json=payload)
            response.raise_for_status() 
            print(f"[SUCCESS] Cursa {trip_id} a fost trimisă la AI.")
    except Exception as e:
        print(f"[ERROR] AI Service a eșuat pentru {trip_id}: {str(e)}")

# 2. Endpoint-ul de procesare (Instant response + Background Task)
@router.post("/process")
async def process_trip(
    body: ProcessTripRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    """
    Primește datele de la Mobile, răspunde INSTANT, 
    și trimite greul către AI în fundal.
    """
    trip_data = {
        **body.dict(),
        "user_id": user["uid"],
        "status": "processing",
    }
    await firestore.save_trip(body.trip_id, trip_data)

    payload = {**body.dict(), "user_id": user["uid"]}
    background_tasks.add_task(send_to_ai_service, body.trip_id, payload)

    return {"trip_id": body.trip_id, "status": "processing", "message": "Trip received and processing in background"}

# 3. Endpoint-urile vechi păstrate intacte
@router.get("/history")
async def get_trip_history(
    limit: int = 20,
    offset: int = 0,
    user=Depends(get_current_user),
):
    """Returnează istoricul curselor pentru utilizatorul autentificat."""
    trips = await firestore.get_user_trips(user["uid"], limit=limit, offset=offset)
    return {"trips": trips, "total": len(trips)}

@router.get("/{trip_id}")
async def get_trip_detail(
    trip_id: str,
    user=Depends(get_current_user),
):
    """Returnează detaliile complete ale unei curse (pentru hartă + raport coach)."""
    trip = await firestore.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if trip.get("user_id") != user["uid"]:
        raise HTTPException(status_code=403, detail="Not your trip")
    return trip