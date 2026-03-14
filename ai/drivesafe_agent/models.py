"""
models.py — Pydantic schemas for DriveSafe
"""
from pydantic import BaseModel
from enum import Enum


class BehaviorType(str, Enum):
    NORMAL = "normal"
    HARD_BRAKE = "hard_brake"
    AGGRESSIVE_ACCEL = "aggressive_accel"
    SHARP_TURN = "sharp_turn"
    LANE_CHANGE = "lane_change"
    TAILGATING = "tailgating"


class RoadType(str, Enum):
    URBAN = "urban"
    HIGHWAY = "highway"
    RURAL = "rural"


class SeverityColor(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class SensorWindow(BaseModel):
    """Feature vector extracted from a 2s sensor data window."""
    accel_x_mean: float = 0.0
    accel_y_mean: float = 0.0
    accel_z_mean: float = 0.0
    accel_magnitude_max: float
    gyro_z_mean: float
    speed_ms: float
    speed_change_rate: float
    lateral_g: float
    heading_change_deg: float


class TripEvent(BaseModel):
    """A single dangerous driving event detected during a trip."""
    event_id: str
    trip_id: str
    behavior_type: BehaviorType
    timestamp: str
    lat: float
    lng: float
    risk_score: float
    severity_color: SeverityColor
    context: dict


class TripSummaryInput(BaseModel):
    """Input for TripSummaryAgent and CoachAgent."""
    trip_id: str
    user_id: str
    start_time: str
    end_time: str
    distance_km: float
    events: list[TripEvent] = []
    gps_polyline: list[dict] = []