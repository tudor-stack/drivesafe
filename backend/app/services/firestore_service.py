"""
app/services/firestore_service.py — Toate operațiunile cu Firestore
Persoana 1 implementează, Persoana 2 (AI) apelează direct Firebase Admin SDK.
"""
import os
import firebase_admin
from firebase_admin import credentials, firestore


class FirestoreService:
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(
                os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "./serviceAccountKey.json")
            )
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    async def save_trip(self, trip_id: str, data: dict):
        self.db.collection("trips").document(trip_id).set(data)

    async def get_trip(self, trip_id: str) -> dict | None:
        doc = self.db.collection("trips").document(trip_id).get()
        return doc.to_dict() if doc.exists else None

    async def get_user_trips(self, user_id: str, limit: int = 20, offset: int = 0) -> list:
        docs = (
            self.db.collection("trips")
            .where("user_id", "==", user_id)
            .where("status", "==", "done")
            .order_by("start_time", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        # Returnăm doar câmpurile necesare pentru lista de istoric
        result = []
        for doc in docs:
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
        self.db.collection("users").document(user_id).set(
            {
                "last_trip_score": score,
                "last_trip_id": trip_id,
                "total_trips": firestore.Increment(1),
            },
            merge=True,
        )
