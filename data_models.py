from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Literal

# --- Core Spatial & Temporal Classes ---

@dataclass
class Waypoint:
    """A single 3D spatial coordinate."""
    x: float
    y: float
    z: float

@dataclass
class TimedWaypoint(Waypoint):
    """
    Represents a specific point in 4D space-time (x, y, z, time).
    Inherits x, y, z from Waypoint.
    """
    time: float

# --- Drone Mission & Schedule Classes ---

@dataclass
class PrimaryMission:
    """
    Defines the mission we are trying to deconflict.
    """
    waypoints: List[Waypoint]
    speed: float  # The drone's constant travel speed (e.g., meters/second)
    mission_start_time: float # The *earliest* the mission can begin
    mission_end_time: float   # The *latest* the mission must be completed

@dataclass
class SimulatedFlight:
    """
    Defines the flight path of *other* drones in the airspace.
    """
    flight_id: str
    # A list of (x, y, z, time) points.
    trajectory: List[TimedWaypoint] 

# --- Output & Reporting Classes ---

@dataclass
class Conflict:
    """A simple structure to hold details of a single conflict."""
    time: float
    location: Waypoint # This is now a 3D Waypoint
    conflicted_with_flight_id: str

@dataclass
class ConflictReport:
    """
    The final output of our deconfliction service.
    """
    status: Literal["CLEAR", "CONFLICT_DETECTED"]
    conflicts: List[Conflict] = field(default_factory=list)