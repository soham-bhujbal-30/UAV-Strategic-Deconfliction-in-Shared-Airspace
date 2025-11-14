from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Literal

# --- Core Spatial & Temporal Classes ---

@dataclass
class Waypoint:
    """A single spatial coordinate in 3D."""
    x: float
    y: float
    z: float  # <<< ADDED FOR 3D

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
    (No changes needed here, it just holds a list of 3D Waypoints)
    """
    waypoints: List[Waypoint]
    speed: float  # The drone's constant travel speed (e.g., meters/second)
    mission_start_time: float # The *earliest* the mission can begin
    mission_end_time: float   # The *latest* the mission must be completed

@dataclass
class SimulatedFlight:
    """
    Defines the flight path of *other* drones in the airspace.
    (No changes needed here, it just holds a list of 3D TimedWaypoints)
    """
    flight_id: str
    trajectory: List[TimedWaypoint] 

# --- Output & Reporting Classes ---

@dataclass
class Conflict:
    """
    Holds details of a single conflict.
    The 'location' is now a 3D Waypoint.
    """
    time: float
    location: Waypoint # This will now automatically contain the z-coordinate
    conflicted_with_flight_id: str

@dataclass
class ConflictReport:
    """
    The final output of our deconfliction service.
    (No changes needed here)
    """
    status: Literal["CLEAR", "CONFLICT DETECTED"]
    conflicts: List[Conflict] = field(default_factory=list)