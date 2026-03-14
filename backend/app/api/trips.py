"""
app/api/trips.py — Endpoints pentru curse
Persoana 1 implementează logica, Persoana 3 (mobile) consumă aceste endpoint-uri.
"""
from fastapi import APIRouter, Depends, HTTPException
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


@router.post("/process")
async def process_trip(
    body: ProcessTripRequest,
    user=Depends(get_current_user),
):
    """
    Primește datele unei curse de la Mobile și le trimite la AI Service.
    Salvează trip-ul cu status 'processing' în Firestore.
    """
    # 1. Salvează trip-ul cu status processing
    trip_data = {
        **body.dict(),
        "user_id": user["uid"],
        "status": "processing",
    }
    await firestore.save_trip(body.trip_id, trip_data)

    # 2. Trimite async la AI Service
    ai_service_url = os.environ.get("AI_SERVICE_URL", "http://localhost:8001")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{ai_service_url}/analyze",
                json={**body.dict(), "user_id": user["uid"]},
            )
    except Exception:
        # AI Service indisponibil — trip-ul rămâne în 'processing', va fi retry
        pass

    return {"trip_id": body.trip_id, "status": "processing", "message": "Trip received"}


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
