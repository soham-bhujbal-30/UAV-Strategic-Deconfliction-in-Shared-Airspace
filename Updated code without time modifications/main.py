from data_models import ConflictReport
from conflict_checker import check_for_conflicts
from scenarios import (
    SCENARIO_CLEAR, 
    SCENARIO_HEAD_ON, 
    SCENARIO_CROSSING,
    SCENARIO_3D_NEAR_MISS, # <<< 3D UPDATE
    SCENARIO_TIME_WINDOW
)
from visualization import animate_simulation 

# --- CONFIGURATION ---
SAFETY_BUFFER = 5.0  # meters
TIME_STEP = 0.5      # seconds (smaller step = more accurate, but slower)

def run_simulation(scenario_name: str, scenario_data: dict, create_animation: bool = False):
    """
    Runs the 3D deconfliction check, prints the result,
    and optionally generates a 3D animation.
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
            # <<< 3D UPDATE (Print x, y, z) >>>
            if "MISSION_TIME_WINDOW" not in conflict.conflicted_with_flight_id:
                loc = (f"(x={conflict.location.x:.2f}, "
                       f"y={conflict.location.y:.2f}, "
                       f"z={conflict.location.z:.2f})")
            else:
                loc = "N/A (Mission time window)"
                
            print(f"  - Time: {conflict.time}s")
            print(f"    Location: {loc}")
            print(f"    With: {conflict.conflicted_with_flight_id}\n")
    
    # --- Generate Animation ---
    if create_animation:
        # Create a unique filename
        # <<< 3D UPDATE (Save as .mp4 since ffmpeg is working) >>>
        vid_filename = f"simulation_{scenario_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}.mp4"
        
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
    
    run_simulation("CLEAR SCENARIO", SCENARIO_CLEAR, create_animation=True)
    run_simulation("HEAD-ON CONFLICT SCENARIO", SCENARIO_HEAD_ON, create_animation=True)
    run_simulation("CROSSING PATH CONFLICT SCENARIO", SCENARIO_CROSSING, create_animation=True)
    
    # <<< 3D UPDATE (Run the extra credit test) >>>
    run_simulation("3D NEAR MISS (ALTITUDE CLEAR)", SCENARIO_3D_NEAR_MISS, create_animation=True)
    
    run_simulation("TIME WINDOW VIOLATION SCENARIO", SCENARIO_TIME_WINDOW, create_animation=False)