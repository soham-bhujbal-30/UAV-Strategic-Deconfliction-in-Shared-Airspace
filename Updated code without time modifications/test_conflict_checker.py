import pytest
from data_models import Waypoint
from conflict_checker import check_for_conflicts
from scenarios import (
    SCENARIO_CLEAR, 
    SCENARIO_HEAD_ON, 
    SCENARIO_CROSSING,
    SCENARIO_TIME_WINDOW,
    SCENARIO_3D_NEAR_MISS
)

# --- CONFIGURATION (Should match main.py) ---
SAFETY_BUFFER = 5.0  # meters
TIME_STEP = 0.5      # seconds

def test_scenario_clear():
    """
    Tests the 3D CLEAR scenario. Expects 'CLEAR' status.
    """
    report = check_for_conflicts(
        primary_mission=SCENARIO_CLEAR["primary_mission"],
        simulated_flights=SCENARIO_CLEAR["simulated_flights"],
        safety_buffer=SAFETY_BUFFER,
        time_step=TIME_STEP
    )
    assert report.status == "CLEAR"
    assert len(report.conflicts) == 0

def test_scenario_head_on_conflict():
    """
    Tests the 3D HEAD-ON conflict. Expects 'CONFLICT DETECTED'.
    """
    report = check_for_conflicts(
        primary_mission=SCENARIO_HEAD_ON["primary_mission"],
        simulated_flights=SCENARIO_HEAD_ON["simulated_flights"],
        safety_buffer=SAFETY_BUFFER,
        time_step=TIME_STEP
    )
    assert report.status == "CONFLICT DETECTED"
    assert len(report.conflicts) > 0
    # Check that the conflict is with the correct drone
    assert report.conflicts[0].conflicted_with_flight_id == "Drone-B (Head-On)"

def test_scenario_crossing_conflict():
    """
    Tests the 3D CROSSING conflict. Expects 'CONFLICT DETECTED'.
    """
    report = check_for_conflicts(
        primary_mission=SCENARIO_CROSSING["primary_mission"],
        simulated_flights=SCENARIO_CROSSING["simulated_flights"],
        safety_buffer=SAFETY_BUFFER,
        time_step=TIME_STEP
    )
    assert report.status == "CONFLICT DETECTED"
    assert len(report.conflicts) > 0
    # Check that the conflict is with the correct drone
    assert report.conflicts[0].conflicted_with_flight_id == "Drone-C (Crossing)"

def test_scenario_3d_near_miss_is_clear():
    """
    *** This is the most important test for 3D. ***
    Tests the 3D NEAR MISS scenario. 
    The drones pass at the same (x, y) but different 'z'.
    Expects 'CLEAR' status because the 3D distance is > safety_buffer.
    """
    report = check_for_conflicts(
        primary_mission=SCENARIO_3D_NEAR_MISS["primary_mission"],
        simulated_flights=SCENARIO_3D_NEAR_MISS["simulated_flights"],
        safety_buffer=SAFETY_BUFFER,
        time_step=TIME_STEP
    )
    assert report.status == "CLEAR"
    assert len(report.conflicts) == 0

def test_scenario_time_window_violation():
    """
    Tests the TIME WINDOW violation. Expects 'CONFLICT DETECTED'.
    """
    report = check_for_conflicts(
        primary_mission=SCENARIO_TIME_WINDOW["primary_mission"],
        simulated_flights=SCENARIO_TIME_WINDOW["simulated_flights"],
        safety_buffer=SAFETY_BUFFER,
        time_step=TIME_STEP
    )
    assert report.status == "CONFLICT DETECTED"
    assert len(report.conflicts) == 1
    # Check that it's the correct type of conflict
    assert report.conflicts[0].conflicted_with_flight_id == "MISSION_TIME_WINDOW_EXCEEDED"