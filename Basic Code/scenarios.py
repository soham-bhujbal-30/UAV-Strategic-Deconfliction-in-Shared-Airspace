from data_models import PrimaryMission, SimulatedFlight, Waypoint, TimedWaypoint

"""
Defines three simulation scenarios for testing the deconfliction system.
"""

# --- COMMON CONSTANTS ---
# Let's define a common primary mission to test against
PRIMARY_MISSION_SPEED = 10.0 # meters / second
PRIMARY_MISSION_WAYPOINTS = [Waypoint(x=0, y=50), Waypoint(x=100, y=50)]
# This mission travels 100 meters at 10 m/s, so it takes 10 seconds.

# --- SCENARIO 1: CLEAR ---
# A simulated drone flies nearby, but at a completely different time.
sim_flight_clear = SimulatedFlight(
    flight_id="Drone-A (Clear)",
    trajectory=[
        TimedWaypoint(x=0, y=60, time=30.0), # Starts at t=30
        TimedWaypoint(x=100, y=60, time=40.0) # Ends at t=40
    ]
)

SCENARIO_CLEAR = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS,
        speed=PRIMARY_MISSION_SPEED,
        mission_start_time=0.0,   # Our mission runs from t=0 to t=10
        mission_end_time=20.0     # Well within the window
    ),
    "simulated_flights": [sim_flight_clear] # Drone-A flies from t=30 to t=40
}


# --- SCENARIO 2: CONFLICT (HEAD-ON) ---
# A simulated drone flies directly towards our drone on the same path.
sim_flight_head_on = SimulatedFlight(
    flight_id="Drone-B (Head-On)",
    trajectory=[
        TimedWaypoint(x=100, y=50, time=0.0), # Starts at t=0 at our end point
        TimedWaypoint(x=0, y=50, time=10.0)   # Flies to our start point
    ]
)

SCENARIO_HEAD_ON = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS,
        speed=PRIMARY_MISSION_SPEED,
        mission_start_time=0.0,   # Our mission: t=0 to t=10
        mission_end_time=20.0
    ),
    "simulated_flights": [sim_flight_head_on] # Drone-B: t=0 to t=10, same path
}


# --- SCENARIO 3: CONFLICT (CROSSING PATH) ---
# A simulated drone crosses our path at the same time.
sim_flight_crossing = SimulatedFlight(
    flight_id="Drone-C (Crossing)",
    trajectory=[
        TimedWaypoint(x=50, y=0, time=0.0),   # Starts at (50, 0) at t=0
        TimedWaypoint(x=50, y=100, time=10.0) # Flies to (50, 100) at t=10
    ]
)

SCENARIO_CROSSING = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS,
        speed=PRIMARY_MISSION_SPEED,
        mission_start_time=0.0,   # Our mission: t=0 to t=10
        mission_end_time=20.0
    ),
    "simulated_flights": [sim_flight_crossing] # Drone-C will be at (50, 50) at t=5
                                               # Our drone will also be at (50, 50) at t=5
}

# --- SCENARIO 4: MISSION TIME WINDOW VIOLATION ---
# Our mission takes 10 seconds, but the window is only 5 seconds.
SCENARIO_TIME_WINDOW = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS,
        speed=PRIMARY_MISSION_SPEED, # Takes 10 seconds
        mission_start_time=0.0,
        mission_end_time=5.0          # ...but must be done by t=5
    ),
    "simulated_flights": [] # No other drones needed
}