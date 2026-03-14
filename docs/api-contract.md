# DriveSafe — API Contract

> **Acesta este documentul de referință pentru toate 3 echipe.**
> Mobile și AI nu vorbesc direct — tot trece prin Backend.
> Orice schimbare de contract se discută cu toată echipa înainte de implementare.

---

## Base URL

- **Local:** `http://localhost:8000`
- **Cloud Run:** `https://drivesafe-backend-xxxx-ew.a.run.app`

## Autentificare

Toate endpoint-urile (exceptând `/health`) necesită header:
```
Authorization: Bearer <firebase_id_token>
```
Mobile obține token-ul din Firebase Auth SDK după login.

---

## Endpoint-uri

### POST `/api/trips/process`
Trimite datele unei curse pentru procesare AI.

**Request body:**
```json
{
  "trip_id": "trip_abc123",
  "start_time": "2026-03-14T10:00:00Z",
  "end_time": "2026-03-14T10:22:00Z",
  "distance_km": 8.4,
  "sensor_windows": [
    {
      "timestamp": "2026-03-14T10:05:00Z",
      "lat": 46.7712,
      "lng": 23.6236,
      "accel_magnitude_max": 4.8,
      "speed_change_rate": -4.5,
      "lateral_g": 0.1,
      "gyro_z_mean": 0.02,
      "speed_ms": 13.8,
      "heading_change_deg": 2.0
    }
  ],
  "gps_polyline": [
    {"lat": 46.7712, "lng": 23.6236, "ts": "2026-03-14T10:00:00Z", "speed_ms": 0}
  ]
}
```

**Response 200:**
```json
{
  "trip_id": "trip_abc123",
  "status": "processing",
  "message": "Trip received, AI pipeline started"
}
```

---

### GET `/api/trips/history`
Returnează lista de curse a utilizatorului autentificat.

**Query params:**
- `limit` (int, default 20)
- `offset` (int, default 0)

**Response 200:**
```json
{
  "trips": [
    {
      "trip_id": "trip_abc123",
      "start_time": "2026-03-14T10:00:00Z",
      "end_time": "2026-03-14T10:22:00Z",
      "distance_km": 8.4,
      "duration_minutes": 22,
      "global_score": 78,
      "events_count": 3,
      "status": "done"
    }
  ],
  "total": 15
}
```

---

### GET `/api/trips/{trip_id}`
Returnează detaliile complete ale unei curse (pentru hartă + raport).

**Response 200:**
```json
{
  "trip_id": "trip_abc123",
  "global_score": 78,
  "start_address": "Str. Memorandumului, Cluj-Napoca",
  "end_address": "Calea Turzii, Cluj-Napoca",
  "gps_polyline": [
    {"lat": 46.7712, "lng": 23.6236, "ts": "...", "speed_ms": 0}
  ],
  "events": [
    {
      "event_id": "ev_001",
      "behavior_type": "hard_brake",
      "timestamp": "2026-03-14T10:05:00Z",
      "lat": 46.7712,
      "lng": 23.6236,
      "risk_score": 7.5,
      "severity_color": "red",
      "context": {
        "road_type": "urban",
        "speed_limit_kmh": 50,
        "speed_actual_kmh": 68
      }
    }
  ],
  "coach_report": "Ai condus în general bine astăzi...",
  "status": "done"
}
```

---

### GET `/api/users/me`
Returnează profilul utilizatorului autentificat.

**Response 200:**
```json
{
  "user_id": "firebase_uid_xxx",
  "display_name": "Tudor",
  "safety_score": 82,
  "total_trips": 15,
  "total_km": 124.3
}
```

---

### GET `/health`
Health check — nu necesită autentificare.

**Response 200:**
```json
{"status": "ok", "service": "drivesafe-backend"}
```

---

## Modele de date partajate

### SeverityColor
`"green"` | `"yellow"` | `"red"`

### BehaviorType
`"normal"` | `"hard_brake"` | `"aggressive_accel"` | `"sharp_turn"` | `"lane_change"` | `"tailgating"`

### TripStatus
`"processing"` | `"done"` | `"failed"`
