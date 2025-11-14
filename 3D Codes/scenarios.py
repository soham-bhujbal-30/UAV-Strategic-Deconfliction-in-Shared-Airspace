from data_models import PrimaryMission, SimulatedFlight, Waypoint, TimedWaypoint

"""
Defines 3D simulation scenarios for testing the deconfliction system.
"""

# --- COMMON CONSTANTS ---
PRIMARY_MISSION_SPEED = 10.0 # meters / second
# Our drone will fly from (0, 50) to (100, 50) at an altitude of 25 meters.
PRIMARY_MISSION_WAYPOINTS_3D = [
    Waypoint(x=0, y=50, z=25), 
    Waypoint(x=100, y=50, z=25)
]
# This mission still travels 100 meters at 10 m/s, so it takes 10 seconds.


# --- SCENARIO 1: 3D CLEAR ---
# A simulated drone flies nearby, but at a completely different time.
sim_flight_clear_3d = SimulatedFlight(
    flight_id="Drone-A (Clear)",
    trajectory=[
        TimedWaypoint(x=0, y=60, z=25, time=30.0), # Starts at t=30
        TimedWaypoint(x=100, y=60, z=25, time=40.0) # Ends at t=40
    ]
)

SCENARIO_CLEAR = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS_3D,
        speed=PRIMARY_MISSION_SPEED,
        mission_start_time=0.0,   # Our mission runs from t=0 to t=10
        mission_end_time=20.0
    ),
    "simulated_flights": [sim_flight_clear_3d]
}


# --- SCENARIO 2: 3D CONFLICT (HEAD-ON) ---
# A simulated drone flies directly towards our drone on the same path
# AT THE SAME ALTITUDE.
sim_flight_head_on_3d = SimulatedFlight(
    flight_id="Drone-B (Head-On)",
    trajectory=[
        TimedWaypoint(x=100, y=50, z=25, time=0.0), # Starts at t=0 at our end point
        TimedWaypoint(x=0, y=50, z=25, time=10.0)   # Flies to our start point
    ]
)

SCENARIO_HEAD_ON = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS_3D,
        speed=PRIMARY_MISSION_SPEED,
        mission_start_time=0.0,   # Our mission: t=0 to t=10
        mission_end_time=20.0
    ),
    "simulated_flights": [sim_flight_head_on_3d]
}


# --- SCENARIO 3: 3D CONFLICT (CROSSING PATH) ---
# A simulated drone crosses our path at the same time
# AT THE SAME ALTITUDE.
sim_flight_crossing_3d = SimulatedFlight(
    flight_id="Drone-C (Crossing)",
    trajectory=[
        TimedWaypoint(x=50, y=0, z=25, time=0.0),   # Starts at (50, 0, 25) at t=0
        TimedWaypoint(x=50, y=100, z=25, time=10.0) # Flies to (50, 100, 25) at t=10
    ]
)

SCENARIO_CROSSING = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS_3D,
        speed=PRIMARY_MISSION_SPEED,
        mission_start_time=0.0,   # Our mission: t=0 to t=10
        mission_end_time=20.0
    ),
    "simulated_flights": [sim_flight_crossing_3d] 
    # Both drones will be at (50, 50, 25) at t=5
}

# --- SCENARIO 4: 3D NEAR MISS (ALTITUDE CLEAR) ---
# *** THIS IS THE KEY 3D TEST ***
# A simulated drone crosses our path at the same (x, y) coordinates and time,
# but at a DIFFERENT ALTITUDE (e.g., 50m vs our 25m).
# Our safety buffer is 5m, so 25m difference is CLEAR.
sim_flight_near_miss_3d = SimulatedFlight(
    flight_id="Drone-D (Near Miss)",
    trajectory=[
        TimedWaypoint(x=50, y=0, z=50, time=0.0),   # Starts at (50, 0, 50) at t=0
        TimedWaypoint(x=50, y=100, z=50, time=10.0) # Flies to (50, 100, 50) at t=10
    ]
)

SCENARIO_3D_NEAR_MISS = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS_3D,
        speed=PRIMARY_MISSION_SPEED,
        mission_start_time=0.0,   # Our mission: t=0 to t=10
        mission_end_time=20.0
    ),
    "simulated_flights": [sim_flight_near_miss_3d]
    # At t=5, our drone is at (50, 50, 25)
    # At t=5, Drone-D is at (50, 50, 50)
    # 2D distance is 0, but 3D distance is 25. This should be CLEAR.
}


# --- SCENARIO 5: MISSION TIME WINDOW VIOLATION ---
# (This scenario is unchanged, but uses the 3D waypoints)
SCENARIO_TIME_WINDOW = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS_3D,
        speed=PRIMARY_MISSION_SPEED, # Takes 10 seconds
        mission_start_time=0.0,
        mission_end_time=5.0          # ...but must be done by t=5
    ),
    "simulated_flights": [] # No other drones needed
}