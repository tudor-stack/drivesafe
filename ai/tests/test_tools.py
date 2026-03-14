"""
tests/test_tools.py — Unit tests for DriveSafe FunctionTools
Run with: pytest tests/ -v
These tests use mock implementations — no Gemini API needed.
"""
import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from drivesafe_agent.tools import (
    get_road_context,
    compute_risk_score,
    save_trip_to_firestore,
)


@pytest.mark.asyncio
async def test_get_road_context_returns_required_fields():
    result = await get_road_context(lat=46.7712, lng=23.6236)
    assert "road_type" in result
    assert "speed_limit_kmh" in result
    assert "near_traffic_light" in result
    assert "context_multiplier" in result


@pytest.mark.asyncio
async def test_compute_risk_score_hard_brake_urban():
    result = await compute_risk_score(
        behavior_type="hard_brake",
        road_type="urban",
        speed_limit_kmh=50.0,
        speed_actual_kmh=55.0,
        near_traffic_light=False,
        context_multiplier=1.0,
    )
    assert result["risk_score"] >= 5.0
    assert result["severity_color"] in ["yellow", "red"]


@pytest.mark.asyncio
async def test_highway_accel_lower_than_urban():
    """Aggressive acceleration on highway should score lower than in urban."""
    highway = await compute_risk_score(
        behavior_type="aggressive_accel",
        road_type="highway",
        speed_limit_kmh=130.0,
        speed_actual_kmh=135.0,
        near_traffic_light=False,
        context_multiplier=0.6,
    )
    urban = await compute_risk_score(
        behavior_type="aggressive_accel",
        road_type="urban",
        speed_limit_kmh=50.0,
        speed_actual_kmh=55.0,
        near_traffic_light=True,
        context_multiplier=1.5,
    )
    assert highway["risk_score"] < urban["risk_score"]


@pytest.mark.asyncio
async def test_save_trip_returns_status():
    result = await save_trip_to_firestore(
        trip_id="test_trip_001",
        summary={"events": [], "global_score": 85, "user_id": "test_user"},
    )
    assert result["status"] == "saved"
    assert result["trip_id"] == "test_trip_001"