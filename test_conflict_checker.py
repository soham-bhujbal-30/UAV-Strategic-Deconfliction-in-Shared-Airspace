import pytest
import json
from data_models import Waypoint, ConflictReport, PrimaryMission, SimulatedFlight, TimedWaypoint
from conflict_checker import check_for_conflicts, convert_mission_to_trajectory
from main import load_scenarios_from_config, SAFETY_BUFFER_HORIZONTAL, SAFETY_BUFFER_VERTICAL

# --- CONFIGURATION ---
TIME_STEP = 0.5
CONFIG_FILE = "config.json"

# --- Fixture to load all scenarios once ---
@pytest.fixture(scope="session")
def all_scenarios():
    """Loads all scenarios from config.json once for all tests."""
    try:
        return load_scenarios_from_config(CONFIG_FILE)
    except Exception as e:
        pytest.fail(f"Failed to load '{CONFIG_FILE}': {e}")



# --- Helper to run the check ---
from typing import List
def run_test_check(mission: PrimaryMission, simulated_flights: List[SimulatedFlight], start_time: float):
    """Helper function to run the conflict check with the cylindrical buffers."""
    primary_trajectory = convert_mission_to_trajectory(mission, start_time)
    return check_for_conflicts(
        primary_trajectory=primary_trajectory,
        mission_end_window=mission.mission_end_time,
        simulated_flights=simulated_flights,
        buffer_horizontal=SAFETY_BUFFER_HORIZONTAL,
        buffer_vertical=SAFETY_BUFFER_VERTICAL,
        time_step=TIME_STEP
    )

# --- Tests for each scenario ---

def test_scenario_clear(all_scenarios):
    scenario = all_scenarios["clear_scenario"]
    report = run_test_check(scenario["primary_mission"], scenario["simulated_flights"], 0.0)
    assert report.status == "CLEAR"

def test_scenario_head_on_conflict(all_scenarios):
    scenario = all_scenarios["head_on_conflict"]
    report = run_test_check(scenario["primary_mission"], scenario["simulated_flights"], 0.0)
    assert report.status == "CONFLICT_DETECTED"
    assert report.conflicts[0].conflicted_with_flight_id == "Drone-B (Head-On)"

def test_scenario_crossing_conflict(all_scenarios):
    scenario = all_scenarios["crossing_conflict"]
    report = run_test_check(scenario["primary_mission"], scenario["simulated_flights"], 0.0)
    assert report.status == "CONFLICT_DETECTED"
    assert report.conflicts[0].conflicted_with_flight_id == "Drone-C (Crossing)"

def test_scenario_3d_near_miss_is_clear(all_scenarios):
    scenario = all_scenarios["near_miss_3d"]
    mission = scenario["primary_mission"]
    # At t=5, primary is at z=50, sim is at z=75.
    # Vertical distance is 25m.
    # Our buffer is 2.0m. 25 > 2, so it should be CLEAR.
    report = run_test_check(mission, scenario["simulated_flights"], 0.0)
    assert report.status == "CLEAR"

def test_scenario_head_on_deconflicted_by_time(all_scenarios):
    """
    Tests the "strategic deconfliction" feature.
    We use the t=10.1s start time, which should be CLEAR.
    """
    scenario = all_scenarios["head_on_conflict"]
    report = run_test_check(scenario["primary_mission"], scenario["simulated_flights"], 10.1)
    # Mission starts 10.1, ends 20.1. Window ends 21.0. This is valid.
    assert report.status == "CLEAR"

def test_cylindrical_buffer_logic(all_scenarios):
    """
    This is the most important test for our new buffer logic.
    It checks 3 drones: H-Close, V-Close, and C-Close.
    Only C-Close (Drone-C) should be a conflict.
    """
    scenario = all_scenarios["cylindrical_test"]
    mission = scenario["primary_mission"]
    
    # We must check at t=5.0s, which is when the sim drones are active
    # Our primary mission's default start time is 0.0, so at t=5.0 it's at (50, 50, 50)
    report = run_test_check(mission, scenario["simulated_flights"], 0.0)
    
    # Check 1: It MUST detect a conflict
    assert report.status == "CONFLICT_DETECTED"
    
    # Check 2: It must have ONLY ONE conflict
    assert len(report.conflicts) == 1
    
    # Check 3: The one conflict it found must be with "Drone-C (CONFLICT)"
    assert report.conflicts[0].conflicted_with_flight_id == "Drone-C (CONFLICT)"