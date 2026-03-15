"""
app/services/firestore_service.py — Toate operațiunile cu Firestore
"""
import os
import firebase_admin
from firebase_admin import credentials, firestore_async
from google.cloud.firestore import Query, Increment # Importuri specifice pentru queries si contoare

class FirestoreService:
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(
                os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json")
            )
            firebase_admin.initialize_app(cred)
        
        # Acum inițializăm clientul ASINCRON, nu cel clasic
        self.db = firestore_async.client()

    async def save_trip(self, trip_id: str, data: dict):
        # Așteptăm (await) răspunsul de la rețea fără să blocăm restul serverului
        await self.db.collection("trips").document(trip_id).set(data)

    async def get_trip(self, trip_id: str) -> dict | None:
        doc = await self.db.collection("trips").document(trip_id).get()
        return doc.to_dict() if doc.exists else None

    async def get_user_trips(self, user_id: str, limit: int = 20, offset: int = 0) -> list:
        # Tot ce e mai jos trebuie sa aiba 4 spatii/1 tab in fata!
        query = (
            self.db.collection("trips")
            .where("user_id", "==", user_id)
            .limit(limit)
        )
        
        result = []
        async for doc in query.stream():
            d = doc.to_dict()
            result.append({
                "trip_id": doc.id,
                "start_time": d.get("start_time"),
                "end_time": d.get("end_time"),
                "distance_km": d.get("distance_km"),
                "global_score": d.get("global_score", 0),
                "events_count": len(d.get("events", [])),
                "status": d.get("status"),
            })
        return result

    async def update_user_score(self, user_id: str, score: float, trip_id: str):
        # Await pe scrierea merge
        await self.db.collection("users").document(user_id).set(
            {
                "last_trip_score": score,
                "last_trip_id": trip_id,
                "total_trips": Increment(1),
            },
            merge=True,
        )