"""
tools.py — FunctionTools for DriveSafe
"""
import os
from google.adk.tools import FunctionTool


async def get_road_context(lat: float, lng: float) -> dict:
    """
    Determines road context for GPS coordinates.

    Args:
        lat: Latitude (ex: 46.7712)
        lng: Longitude (ex: 23.6236)

    Returns:
        dict with road_type, speed_limit_kmh, near_traffic_light, context_multiplier
    """
    # TODO: replace with Google Roads API
    return {
        "road_type": "urban",
        "speed_limit_kmh": 50.0,
        "near_traffic_light": False,
        "context_multiplier": 1.0,
        "zone_description": "Urban area, standard speed limit",
    }


async def compute_risk_score(
    behavior_type: str,
    road_type: str,
    speed_limit_kmh: float,
    speed_actual_kmh: float,
    near_traffic_light: bool,
    context_multiplier: float,
) -> dict:
    """
    Calculates contextual risk score for a dangerous behavior.

    Args:
        behavior_type: Detected behavior type
        road_type: Road type (urban, highway, rural)
        speed_limit_kmh: Posted speed limit
        speed_actual_kmh: Actual speed at event
        near_traffic_light: Traffic signal within 50m
        context_multiplier: Multiplier from road context

    Returns:
        dict with risk_score (1-10), severity_color, explanation
    """
    BASE_SEVERITY = {
        "hard_brake": 7.0,
        "aggressive_accel": 6.0,
        "sharp_turn": 5.0,
        "lane_change": 6.0,
        "tailgating": 8.0,
        "normal": 0.0,
    }

    base = BASE_SEVERITY.get(behavior_type, 5.0)

    if near_traffic_light:
        context_multiplier *= 1.5
    if road_type == "highway" and behavior_type == "aggressive_accel":
        context_multiplier *= 0.6
    if speed_actual_kmh > speed_limit_kmh * 1.3:
        context_multiplier *= 1.3

    score = min(10.0, round(base * context_multiplier, 1))

    if score >= 7.5:
        color = "red"
    elif score >= 4.5:
        color = "yellow"
    else:
        color = "green"

    return {
        "risk_score": score,
        "severity_color": color,
        "explanation": (
            f"{behavior_type} on {road_type} road "
            f"(limit {speed_limit_kmh}km/h, actual {speed_actual_kmh}km/h) "
            f"= score {score}/10"
        ),
    }


async def save_trip_to_firestore(trip_id: str, summary: dict) -> dict:
    """
    Saves processed trip to Firestore and updates user profile.

    Args:
        trip_id: Unique trip identifier
        summary: Complete dict with all processed trip data

    Returns:
        dict with status and trip_id
    """
    import firebase_admin
    from firebase_admin import credentials, firestore

    if not firebase_admin._apps:
        cred = credentials.Certificate(
            os.environ.get(
                "GOOGLE_APPLICATION_CREDENTIALS",
                "./serviceAccountKey.json"
            )
        )
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    db.collection("trips").document(trip_id).set(summary)

    user_id = summary.get("user_id", "unknown")
    db.collection("users").document(user_id).set(
        {
            "last_trip_id": trip_id,
            "last_trip_score": summary.get("global_score", 0),
            "total_trips": firebase_admin.firestore.Increment(1),
        },
        merge=True,
    )

    print(f"[Firestore] Trip {trip_id} saved successfully")
    return {
        "status": "saved",
        "trip_id": trip_id,
        "events_count": len(summary.get("events", [])),
    }


async def send_fcm_notification(user_id: str, title: str, body: str) -> dict:
    """
    Sends push notification via Firebase Cloud Messaging.

    Args:
        user_id: Firebase user ID
        title: Notification title
        body: Notification body
    """
    # TODO: replace with real Firebase Admin SDK FCM
    print(f"[FCM] -> user {user_id}: {title} - {body}")
    return {"status": "sent", "user_id": user_id}


# Wrap with FunctionTool
get_road_context_tool = FunctionTool(get_road_context)
compute_risk_score_tool = FunctionTool(compute_risk_score)
save_trip_to_firestore_tool = FunctionTool(save_trip_to_firestore)
send_fcm_notification_tool = FunctionTool(send_fcm_notification)