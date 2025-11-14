from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Literal

# --- Core Spatial & Temporal Classes ---

@dataclass
class Waypoint:
    """A single spatial coordinate. We'll add 'z' here for 3D."""
    x: float
    y: float
    # z: float = 0.0  # Reserved for 3D Extra Credit

@dataclass
class TimedWaypoint(Waypoint):
    """
    Represents a specific point in 4D space-time (x, y, time).
    This is the fundamental unit for our conflict check.
    We'll inherit x and y from Waypoint.
    """
    time: float

# --- Drone Mission & Schedule Classes ---

@dataclass
class PrimaryMission:
    """
    Defines the mission we are trying to deconflict.
    It's a set of waypoints, a speed, and an overall time window.
    """
    waypoints: List[Waypoint]
    speed: float  # The drone's constant travel speed (e.g., meters/second)
    mission_start_time: float # The *earliest* the mission can begin
    mission_end_time: float   # The *latest* the mission must be completed

@dataclass
class SimulatedFlight:
    """
    Defines the flight path of *other* drones in the airspace.
    We'll represent their paths as a discrete list of timed waypoints.
    This is a crucial design choice: it makes conflict checking
    a simple "lookup" problem instead of complex geometry.
    """
    flight_id: str
    # A list of (x, y, time) points. We assume linear interpolation 
    # for times between these points.
    trajectory: List[TimedWaypoint] 

# --- Output & Reporting Classes ---

@dataclass
class Conflict:
    """A simple structure to hold details of a single conflict."""
    time: float
    location: Waypoint
    conflicted_with_flight_id: str

@dataclass
class ConflictReport:
    """
    The final output of our deconfliction service.
    """
    status: Literal["CLEAR", "CONFLICT DETECTED"]
    conflicts: List[Conflict] = field(default_factory=list)