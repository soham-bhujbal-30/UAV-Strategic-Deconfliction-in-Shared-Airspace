import math
from typing import List, Optional
from data_models import (
    Waypoint, 
    TimedWaypoint, 
    PrimaryMission, 
    SimulatedFlight, 
    Conflict, 
    ConflictReport
)

# --- Helper Functions ---

def calculate_distance(wp1: Waypoint, wp2: Waypoint) -> float:
    """Calculates the 2D Euclidean distance between two waypoints."""
    # We'll update this for 3D later by adding (wp1.z - wp2.z)**2
    return math.sqrt((wp1.x - wp2.x)**2 + (wp1.y - wp2.y)**2)

def interpolate_position(start_wp: TimedWaypoint, end_wp: TimedWaypoint, current_time: float) -> Waypoint:
    """
    Linearly interpolates the (x, y) position of a drone at a specific time,
    given its start and end TimedWaypoints.
    """
    
    # Handle edge case: if time is outside the segment, return the boundary
    if current_time <= start_wp.time:
        return Waypoint(x=start_wp.x, y=start_wp.y)
    if current_time >= end_wp.time:
        return Waypoint(x=end_wp.x, y=end_wp.y)

    # Calculate fraction of time elapsed in this segment
    segment_duration = end_wp.time - start_wp.time
    # Avoid division by zero if start and end time are the same
    if segment_duration == 0:
        return Waypoint(x=start_wp.x, y=start_wp.y)
        
    time_elapsed = current_time - start_wp.time
    fraction = time_elapsed / segment_duration

    # Linearly interpolate x and y
    interp_x = start_wp.x + (end_wp.x - start_wp.x) * fraction
    interp_y = start_wp.y + (end_wp.y - start_wp.y) * fraction
    
    return Waypoint(x=interp_x, y=interp_y)

# --- Core Logic Functions ---

def _convert_mission_to_trajectory(mission: PrimaryMission) -> List[TimedWaypoint]:
    """
    Converts a PrimaryMission (waypoints + speed) into a discrete
    time-based trajectory (list of TimedWaypoints).
    
    This trajectory starts at the mission.mission_start_time.
    """
    trajectory = []
    current_time = mission.mission_start_time
    
    if not mission.waypoints:
        return []

    # Add the first waypoint at the start time
    first_wp = mission.waypoints[0]
    trajectory.append(TimedWaypoint(x=first_wp.x, y=first_wp.y, time=current_time))

    # Iterate through the rest of the waypoints
    for i in range(len(mission.waypoints) - 1):
        wp1 = mission.waypoints[i]
        wp2 = mission.waypoints[i+1]
        
        distance = calculate_distance(wp1, wp2)
        
        # This check is crucial for handling zero speed or zero distance
        if mission.speed <= 0:
            # If speed is zero, all subsequent waypoints are at the start time (or just add the first one)
            # For this problem, we'll assume speed is positive.
            # If not, we could raise an error.
            if distance > 0:
                raise ValueError("Cannot travel between waypoints with zero or negative speed.")
            # If distance is also 0, just add the next waypoint at the same time
            if not any(t.x == wp2.x and t.y == wp2.y for t in trajectory):
                 trajectory.append(TimedWaypoint(x=wp2.x, y=wp2.y, time=current_time))
            continue
            
        time_to_travel = distance / mission.speed
        current_time += time_to_travel
        
        trajectory.append(TimedWaypoint(x=wp2.x, y=wp2.y, time=current_time))
        
    return trajectory

def _find_drone_position(trajectory: List[TimedWaypoint], current_time: float) -> Optional[Waypoint]:
    """
    Finds a drone's (x, y) position at a specific time from its trajectory.
    
    Returns None if the time is outside the trajectory's bounds.
    """
    # Find the two waypoints that bracket the current_time
    for i in range(len(trajectory) - 1):
        wp_start = trajectory[i]
        wp_end = trajectory[i+1]
        
        if wp_start.time <= current_time <= wp_end.time:
            return interpolate_position(wp_start, wp_end, current_time)
            
    # If time is before the trajectory starts or after it ends,
    # the drone is not considered to be in the active airspace for this check.
    return None

# --- Main Public Function ---

def check_for_conflicts(
    primary_mission: PrimaryMission, 
    simulated_flights: List[SimulatedFlight], 
    safety_buffer: float, 
    time_step: float = 1.0
) -> ConflictReport:
    """
    Main deconfliction function.
    
    Simulates the airspace in discrete time steps and checks for 
    spatial conflicts (breach of safety_buffer).
    """
    
    # 1. Convert our primary mission into a time-based path
    try:
        primary_trajectory = _convert_mission_to_trajectory(primary_mission)
    except ValueError as e:
        return ConflictReport(status="CONFLICT DETECTED", conflicts=[
            Conflict(time=0, location=Waypoint(0,0), conflicted_with_flight_id=f"Mission Error: {e}")
        ])

    if not primary_trajectory:
        return ConflictReport(status="CLEAR") # No mission to check

    mission_start = primary_trajectory[0].time
    mission_end = primary_trajectory[-1].time

    # 2. Check if the *calculated* mission time exceeds the *allowed* window
    if mission_end > primary_mission.mission_end_time:
        return ConflictReport(
            status="CONFLICT DETECTED",
            conflicts=[Conflict(
                time=mission_end,
                location=primary_trajectory[-1],
                conflicted_with_flight_id="MISSION_TIME_WINDOW_EXCEEDED"
            )]
        )

    all_conflicts = []
    
    # 3. Simulate! Iterate through time, step by step.
    current_time = mission_start
    while current_time <= mission_end:
        
        # 4. Find our primary drone's position at this time
        primary_pos = _find_drone_position(primary_trajectory, current_time)
        if primary_pos is None:
            # This shouldn't happen based on our loop, but good to check
            current_time += time_step
            continue

        # 5. Check against EVERY simulated drone's position at this same time
        for sim_flight in simulated_flights:
            sim_pos = _find_drone_position(sim_flight.trajectory, current_time)
            
            if sim_pos is None:
                # This simulated drone is not flying at this time, so no conflict
                continue
            
            # 6. The actual spatial check!
            distance = calculate_distance(primary_pos, sim_pos)
            
            if distance < safety_buffer:
                # CONFLICT DETECTED!
                conflict = Conflict(
                    time=round(current_time, 2),
                    location=primary_pos,
                    conflicted_with_flight_id=sim_flight.flight_id
                )
                all_conflicts.append(conflict)

        current_time += time_step

    # 7. Final Report
    if all_conflicts:
        # We can add logic here to de-duplicate or clean up conflicts
        # For now, just return them all
        return ConflictReport(status="CONFLICT DETECTED", conflicts=all_conflicts)
    
    return ConflictReport(status="CLEAR")