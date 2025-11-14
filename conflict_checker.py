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
    """Calculates the 3D Euclidean distance between two waypoints."""
    return math.sqrt((wp1.x - wp2.x)**2 + (wp1.y - wp2.y)**2 + (wp1.z - wp2.z)**2)

def interpolate_position(start_wp: TimedWaypoint, end_wp: TimedWaypoint, current_time: float) -> Waypoint:
    """
    Linearly interpolates the (x, y, z) position of a drone at a specific time.
    """
    if current_time <= start_wp.time:
        return Waypoint(x=start_wp.x, y=start_wp.y, z=start_wp.z)
    if current_time >= end_wp.time:
        return Waypoint(x=end_wp.x, y=end_wp.y, z=end_wp.z)

    segment_duration = end_wp.time - start_wp.time
    if segment_duration == 0:
        return Waypoint(x=start_wp.x, y=start_wp.y, z=start_wp.z)
        
    time_elapsed = current_time - start_wp.time
    fraction = time_elapsed / segment_duration

    interp_x = start_wp.x + (end_wp.x - start_wp.x) * fraction
    interp_y = start_wp.y + (end_wp.y - start_wp.y) * fraction
    interp_z = start_wp.z + (end_wp.z - start_wp.z) * fraction
    
    return Waypoint(x=interp_x, y=interp_y, z=interp_z)

# --- Core Logic Functions ---

def convert_mission_to_trajectory(mission: PrimaryMission, actual_start_time: float) -> List[TimedWaypoint]:
    """
    Converts a PrimaryMission (waypoints + speed) into a discrete
    time-based trajectory (list of TimedWaypoints) based on a
    user-provided start time.
    """
    trajectory = []
    current_time = actual_start_time
    
    if not mission.waypoints:
        return []

    first_wp = mission.waypoints[0]
    trajectory.append(TimedWaypoint(x=first_wp.x, y=first_wp.y, z=first_wp.z, time=current_time))

    for i in range(len(mission.waypoints) - 1):
        wp1 = mission.waypoints[i]
        wp2 = mission.waypoints[i+1]
        
        distance = calculate_distance(wp1, wp2)
        
        if mission.speed <= 0:
            if distance > 0:
                raise ValueError("Cannot travel between waypoints with zero or negative speed.")
            if not any(t.x == wp2.x and t.y == wp2.y and t.z == wp2.z for t in trajectory):
                 trajectory.append(TimedWaypoint(x=wp2.x, y=wp2.y, z=wp2.z, time=current_time))
            continue
            
        time_to_travel = distance / mission.speed
        current_time += time_to_travel
        
        trajectory.append(TimedWaypoint(x=wp2.x, y=wp2.y, z=wp2.z, time=current_time))
        
    return trajectory

def _find_drone_position(trajectory: List[TimedWaypoint], current_time: float) -> Optional[Waypoint]:
    """
    Finds a drone's (x, y, z) position at a specific time from its trajectory.
    """
    for i in range(len(trajectory) - 1):
        wp_start = trajectory[i]
        wp_end = trajectory[i+1]
        
        if wp_start.time <= current_time <= wp_end.time:
            return interpolate_position(wp_start, wp_end, current_time)
            
    return None

def check_for_conflicts(
    primary_trajectory: List[TimedWaypoint], 
    mission_end_window: float,              
    simulated_flights: List[SimulatedFlight], 
    buffer_horizontal: float, # <<< UPDATED
    buffer_vertical: float,   # <<< UPDATED
    time_step: float = 1.0
) -> ConflictReport:
    """
    Main deconfliction function with cylindrical safety buffer.
    """
    
    if not primary_trajectory:
        return ConflictReport(status="CLEAR")

    mission_start = primary_trajectory[0].time
    mission_end = primary_trajectory[-1].time

    if mission_end > mission_end_window:
        return ConflictReport(
            status="CONFLICT_DETECTED",
            conflicts=[Conflict(
                time=mission_end,
                location=primary_trajectory[-1],
                conflicted_with_flight_id="MISSION_TIME_WINDOW_EXCEEDED"
            )]
        )

    all_conflicts = []
    
    current_time = mission_start
    while current_time <= mission_end: 
        
        primary_pos = _find_drone_position(primary_trajectory, current_time)
        if primary_pos is None:
            current_time += time_step
            continue

        for sim_flight in simulated_flights:
            sim_pos = _find_drone_position(sim_flight.trajectory, current_time)
            
            if sim_pos is None:
                continue
            
            # --- NEW CYLINDRICAL CHECK ---
            dx = primary_pos.x - sim_pos.x
            dy = primary_pos.y - sim_pos.y
            dz_vertical = abs(primary_pos.z - sim_pos.z)
            
            dist_horizontal_sq = dx*dx + dy*dy
            buffer_horizontal_sq = buffer_horizontal * buffer_horizontal
            
            if (dist_horizontal_sq < buffer_horizontal_sq) and (dz_vertical < buffer_vertical):
                conflict = Conflict(
                    time=round(current_time, 2),
                    location=primary_pos,
                    conflicted_with_flight_id=sim_flight.flight_id
                )
                all_conflicts.append(conflict)
            # --- END OF NEW CHECK ---

        current_time += time_step

    if all_conflicts:
        unique_conflicts = []
        seen_ids_at_time = set()
        for conflict in all_conflicts:
            key = (conflict.conflicted_with_flight_id, conflict.time)
            if key not in seen_ids_at_time:
                unique_conflicts.append(conflict)
                seen_ids_at_time.add(key)
        
        return ConflictReport(status="CONFLICT_DETECTED", conflicts=unique_conflicts)
    
    return ConflictReport(status="CLEAR")