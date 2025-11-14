from data_models import PrimaryMission, SimulatedFlight, Waypoint, TimedWaypoint

"""
Defines 3D (4D) simulation scenarios for testing the deconfliction system.
"""

# --- COMMON CONSTANTS ---
PRIMARY_MISSION_SPEED = 10.0 # meters / second
# Our primary mission flies from (0,50) to (100,50) at an altitude of 50m
PRIMARY_MISSION_WAYPOINTS_3D = [
    Waypoint(x=0, y=50, z=50), 
    Waypoint(x=100, y=50, z=50)
]
# This mission still takes 10 seconds (100m at 10 m/s).
# The allowed time window for the mission is t=0.0 to t=20.0
PRIMARY_MISSION_TIME_WINDOW_START = 0.0
PRIMARY_MISSION_TIME_WINDOW_END = 20.0


# --- SCENARIO 1: CLEAR ---
sim_flight_clear = SimulatedFlight(
    flight_id="Drone-A (Clear)",
    trajectory=[
        TimedWaypoint(x=0, y=60, z=50, time=30.0), # Starts at t=30
        TimedWaypoint(x=100, y=60, z=50, time=40.0) # Ends at t=40
    ]
)
SCENARIO_CLEAR = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS_3D,
        speed=PRIMARY_MISSION_SPEED,
        mission_start_time=PRIMARY_MISSION_TIME_WINDOW_START,
        mission_end_time=PRIMARY_MISSION_TIME_WINDOW_END     
    ),
    "simulated_flights": [sim_flight_clear] 
}


# --- SCENARIO 2: CONFLICT (HEAD-ON) ---
sim_flight_head_on = SimulatedFlight(
    flight_id="Drone-B (Head-On)",
    trajectory=[
        TimedWaypoint(x=100, y=50, z=50, time=0.0), # Starts at our end point
        TimedWaypoint(x=0, y=50, z=50, time=10.0)   # Flies to our start point
    ]
)
SCENARIO_HEAD_ON = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS_3D,
        speed=PRIMARY_MISSION_SPEED,
        mission_start_time=PRIMARY_MISSION_TIME_WINDOW_START,
        mission_end_time=PRIMARY_MISSION_TIME_WINDOW_END
    ),
    "simulated_flights": [sim_flight_head_on]
}


# --- SCENARIO 3: CONFLICT (CROSSING PATH) ---
sim_flight_crossing = SimulatedFlight(
    flight_id="Drone-C (Crossing)",
    trajectory=[
        TimedWaypoint(x=50, y=0, z=50, time=0.0),   
        TimedWaypoint(x=50, y=100, z=50, time=10.0) 
    ]
)
SCENARIO_CROSSING = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS_3D,
        speed=PRIMARY_MISSION_SPEED,
        mission_start_time=PRIMARY_MISSION_TIME_WINDOW_START,
        mission_end_time=PRIMARY_MISSION_TIME_WINDOW_END
    ),
    "simulated_flights": [sim_flight_crossing] # Both at (50, 50, 50) at t=5
}

# --- SCENARIO 4: 3D NEAR MISS (ALTITUDE CLEAR) ---
sim_flight_near_miss = SimulatedFlight(
    flight_id="Drone-D (Near Miss)",
    trajectory=[
        TimedWaypoint(x=50, y=0, z=75, time=0.0),   # Flies at 75m altitude
        TimedWaypoint(x=50, y=100, z=75, time=10.0) 
    ]
)
SCENARIO_3D_NEAR_MISS = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS_3D, # Our drone is at 50m altitude
        speed=PRIMARY_MISSION_SPEED,
        mission_start_time=PRIMARY_MISSION_TIME_WINDOW_START,
        mission_end_time=PRIMARY_MISSION_TIME_WINDOW_END
    ),
    "simulated_flights": [sim_flight_near_miss] # Other drone is at 75m
}

# --- SCENARIO 5: MISSION TIME WINDOW VIOLATION ---
SCENARIO_TIME_WINDOW = {
    "primary_mission": PrimaryMission(
        waypoints=PRIMARY_MISSION_WAYPOINTS_3D,
        speed=PRIMARY_MISSION_SPEED, # Takes 10 seconds
        mission_start_time=0.0,
        mission_end_time=5.0          # ...but must be done by t=5
    ),
    "simulated_flights": [] 
}