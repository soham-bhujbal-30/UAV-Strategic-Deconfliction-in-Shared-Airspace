import json
from data_models import ConflictReport
from conflict_checker import check_for_conflicts
from scenarios import (
    SCENARIO_CLEAR, 
    SCENARIO_HEAD_ON, 
    SCENARIO_CROSSING,
    SCENARIO_TIME_WINDOW
)
# Import the new animation function
from visualization import animate_simulation 

# --- CONFIGURATION ---
SAFETY_BUFFER = 5.0  # meters
TIME_STEP = 0.5      # seconds (smaller step = more accurate, but slower)

def run_simulation(scenario_name: str, scenario_data: dict, create_animation: bool = False):
    """
    Runs the deconfliction check for a given scenario, prints the result,
    and optionally generates an animation.
    """
    print("---" * 20)
    print(f"🚀 RUNNING SIMULATION: {scenario_name}")
    print("---" * 20)
    
    report = check_for_conflicts(
        primary_mission=scenario_data["primary_mission"],
        simulated_flights=scenario_data["simulated_flights"],
        safety_buffer=SAFETY_BUFFER,
        time_step=TIME_STEP
    )
    
    # --- Pretty Print Report ---
    print(f"✅ STATUS: {report.status}\n")
    
    if report.status == "CONFLICT DETECTED":
        print("🔥 CONFLICT DETAILS:")
        for conflict in report.conflicts:
            # Format location nicely
            if "MISSION_TIME_WINDOW" not in conflict.conflicted_with_flight_id:
                loc = f"(x={conflict.location.x:.2f}, y={conflict.location.y:.2f})"
            else:
                loc = "N/A"
                
            print(f"  - Time: {conflict.time}s")
            print(f"    Location: {loc}")
            print(f"    With: {conflict.conflicted_with_flight_id}\n")
    
    # --- Generate Animation ---
    if create_animation:
        # Create a unique filename for each animation
        vid_filename = f"simulation_{scenario_name.lower().replace(' ', '_')}.gif"
        
        # We need to update visualization.py to accept a filename
        # For now, let's just modify the visualization.py code...
        # ... (Self-correction: No, let's just call it. 
        # The current visualization.py saves as "simulation.mp4". 
        # We should improve that.)
        
        # Let's assume visualization.py is updated to take a filename
        # (I will provide the updated visualization.py next if you agree)
        
        # For now, let's just call it. The file will be overwritten each time.
        # This is simpler.
       # Create a unique filename
        vid_filename = f"simulation_{scenario_name.lower().replace(' ', '_')}.mp4"
        
        animate_simulation(
            scenario_data["primary_mission"],
            scenario_data["simulated_flights"],
            report,
            scenario_name,
            output_filename=vid_filename # Pass the unique filename
        )
        
    print("\n")


if __name__ == "__main__":
    # --- CHOOSE WHICH SCENARIOS TO RUN ---
    
    # Set create_animation=True for the scenarios you want to record
    run_simulation("CLEAR SCENARIO", SCENARIO_CLEAR, create_animation=True)
    run_simulation("HEAD-ON CONFLICT SCENARIO", SCENARIO_HEAD_ON, create_animation=True)
    run_simulation("CROSSING PATH CONFLICT SCENARIO", SCENARIO_CROSSING, create_animation=True)
    run_simulation("TIME WINDOW VIOLATION SCENARIO", SCENARIO_TIME_WINDOW, create_animation=False) # No need to animate this