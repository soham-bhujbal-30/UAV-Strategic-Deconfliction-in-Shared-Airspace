import json
import math
from data_models import PrimaryMission, SimulatedFlight, Waypoint, TimedWaypoint
from typing import List, Dict, Optional
from conflict_checker import check_for_conflicts, convert_mission_to_trajectory
from visualization import animate_simulation 

# --- CONFIGURATION ---
SAFETY_BUFFER_HORIZONTAL = 5.0  # meters
SAFETY_BUFFER_VERTICAL = 2.0    # meters
TIME_STEP = 0.5                 # seconds
CONFIG_FILE = "config.json"

def load_scenarios_from_config(config_path: str) -> Dict[str, dict]:
    """
    Loads all scenarios from a JSON config file and
    converts them into our dataclasses.
    """
    print(f"Loading all scenarios from '{config_path}'...")
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    parsed_scenarios = {}
    
    for key, scenario in config_data.items():
        try:
            pm_data = scenario["primary_mission"]
            primary_mission = PrimaryMission(
                waypoints=[Waypoint(**wp) for wp in pm_data["waypoints"]],
                speed=pm_data["speed"],
                mission_start_time=pm_data["mission_start_time"],
                mission_end_time=pm_data["mission_end_time"]
            )
            sim_flights = []
            for flight_data in scenario["simulated_flights"]:
                sim_flights.append(
                    SimulatedFlight(
                        flight_id=flight_data["flight_id"],
                        trajectory=[TimedWaypoint(**wp) for wp in flight_data["trajectory"]]
                    )
                )
            parsed_scenarios[key] = {
                "scenario_name": scenario["scenario_name"],
                "primary_mission": primary_mission,
                "simulated_flights": sim_flights
            }
        except Exception as e:
            print(f"Warning: Could not parse scenario '{key}'. Error: {e}")
            
    return parsed_scenarios

def run_simulation(
    scenario_name: str,
    primary_mission: PrimaryMission,
    simulated_flights: List[SimulatedFlight],
    desired_start_time: float, 
    create_animation: bool = False
):
    """
    Runs the 3D deconfliction check for a user-defined start time.
    """
    print("---" * 20)
    print(f"🚀 RUNNING SIMULATION: {scenario_name}")
    print(f"    Desired Start Time: {desired_start_time}s")
    print(f"    Using Buffers: H={SAFETY_BUFFER_HORIZONTAL}m, V={SAFETY_BUFFER_VERTICAL}m")
    print("---" * 20)
    
    if desired_start_time < primary_mission.mission_start_time:
        print(f"❌ STATUS: REJECTED")
        print(f"   REASON: Desired start time {desired_start_time}s is before "
              f"allowed window start of {primary_mission.mission_start_time}s.\n")
        return

    try:
        primary_trajectory = convert_mission_to_trajectory(
            primary_mission, 
            desired_start_time
        )
    except ValueError as e:
        print(f"❌ STATUS: REJECTED")
        print(f"   REASON: {e}\n")
        return
        
    report = check_for_conflicts(
        primary_trajectory=primary_trajectory,
        mission_end_window=primary_mission.mission_end_time,
        simulated_flights=simulated_flights,
        buffer_horizontal=SAFETY_BUFFER_HORIZONTAL,
        buffer_vertical=SAFETY_BUFFER_VERTICAL,
        time_step=TIME_STEP
    )
    
    print(f"✅ STATUS: {report.status}\n")
    
    if report.status == "CONFLICT_DETECTED":
        print("🔥 CONFLICT DETAILS:")
        for conflict in report.conflicts:
            if "MISSION_TIME_WINDOW" not in conflict.conflicted_with_flight_id:
                loc = (f"(x={conflict.location.x:.2f}, "
                       f"y={conflict.location.y:.2f}, "
                       f"z={conflict.location.z:.2f})")
            else:
                loc = "N/A (Mission time window)"
                
            print(f"  - Time: {conflict.time}s")
            print(f"    Location: {loc}")
            print(f"    With: {conflict.conflicted_with_flight_id}\n")
    
    if create_animation:
        vid_filename = (f"simulation_{scenario_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
                        f"_t_start_{desired_start_time}.mp4")
        
        animate_simulation(
            primary_trajectory=primary_trajectory, 
            simulated_flights=simulated_flights,
            conflict_report=report,
            scenario_name=f"{scenario_name} (Start: {desired_start_time}s)",
            output_filename=vid_filename
        )
    
    print("\n")

def change_safety_buffers():
    global SAFETY_BUFFER_HORIZONTAL, SAFETY_BUFFER_VERTICAL
    print("\n" + "---" * 10)
    print("   Change Safety Buffers")
    print("---" * 10)
    print(f"Current Horizontal Buffer: {SAFETY_BUFFER_HORIZONTAL}m")
    print(f"Current Vertical Buffer: {SAFETY_BUFFER_VERTICAL}m")
    
    try:
        new_h_input = input(f"Enter new HORIZONTAL buffer (or press Enter to keep {SAFETY_BUFFER_HORIZONTAL}m): ")
        if new_h_input.strip():
            new_h = float(new_h_input)
            if new_h < 0:
                print("Buffer cannot be negative. No changes made.")
            else:
                SAFETY_BUFFER_HORIZONTAL = new_h
                print(f"✅ Horizontal buffer updated to {SAFETY_BUFFER_HORIZONTAL}m")

        new_v_input = input(f"Enter new VERTICAL buffer (or press Enter to keep {SAFETY_BUFFER_VERTICAL}m): ")
        if new_v_input.strip():
            new_v = float(new_v_input)
            if new_v < 0:
                print("Buffer cannot be negative. No changes made.")
            else:
                SAFETY_BUFFER_VERTICAL = new_v
                print(f"✅ Vertical buffer updated to {SAFETY_BUFFER_VERTICAL}m")

    except ValueError:
        print("❌ Invalid input. Please enter a number. Buffers not changed.")
    
    print("---" * 10)
    print("\nPress Enter to return to main menu.")
    input()

def _get_user_input_float(prompt: str) -> float:
    while True:
        try:
            value_str = input(prompt)
            value = float(value_str)
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def _get_user_input_waypoint(prompt: str) -> Waypoint:
    while True:
        try:
            value_str = input(prompt)
            parts = value_str.split(',')
            if len(parts) != 3:
                raise ValueError("Input must have 3 parts (x, y, z).")
            x = float(parts[0].strip())
            y = float(parts[1].strip())
            z = float(parts[2].strip())
            return Waypoint(x=x, y=y, z=z)
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter in the format 'x, y, z' (e.g., '100, 50, 50')")

def create_mission_wizard() -> Optional[PrimaryMission]:
    print("\n" + "---" * 10)
    print("   CREATE NEW PRIMARY MISSION WIZARD")
    print("---" * 10)
    
    try:
        speed = _get_user_input_float("Enter drone speed (e.g., 10.0): ")
        if speed <= 0:
            print("Speed must be positive. Aborting mission creation.")
            return None

        waypoints = []
        print("\nEnter at least 2 waypoints in 'x, y, z' format (e.g., '0, 50, 50')")
        
        wp1 = _get_user_input_waypoint("Enter Waypoint 1: ")
        waypoints.append(wp1)
        
        wp_num = 2
        while True:
            if wp_num > 2:
                add_more = input(f"Add another waypoint (Waypoint {wp_num})? (y/n): ").lower().strip()
                if add_more != 'y':
                    break
            
            wp_next = _get_user_input_waypoint(f"Enter Waypoint {wp_num}: ")
            waypoints.append(wp_next)
            wp_num += 1

        start_window = _get_user_input_float("Enter mission start window (e.g., 0.0): ")
        end_window = _get_user_input_float(f"Enter mission end window (e.g., 20.0): ")
        if end_window <= start_window:
            print("End window must be after start window. Aborting.")
            return None
        
        new_mission = PrimaryMission(
            waypoints=waypoints,
            speed=speed,
            mission_start_time=start_window,
            mission_end_time=end_window
        )
        print("---" * 10)
        print("✅ New temporary mission created successfully.")
        return new_mission

    except Exception as e:
        print(f"\nAn error occurred during mission creation: {e}. Aborting.")
        return None

if __name__ == "__main__":
    
    try:
        all_scenarios = load_scenarios_from_config(CONFIG_FILE)
        if not all_scenarios:
            raise Exception("No valid scenarios were loaded.")
    except FileNotFoundError:
        print(f"Error: Could not find '{CONFIG_FILE}'. Please create it.")
        exit()
    except Exception as e:
        print(f"Error parsing '{CONFIG_FILE}': {e}")
        exit()

    while True:
        print("\n" + "===" * 20)
        print("    UAV STRATEGIC DECONFLICTION TOOL - MAIN MENU")
        print("===" * 20)
        print("Please choose an option:")
        
        scenario_keys = list(all_scenarios.keys())
        # --- MENU OPTION 1 ---
        print("\n[ Run a Scenario from config.json ]")
        for i, key in enumerate(scenario_keys):
            print(f"  {i+1}: Run '{all_scenarios[key]['scenario_name']}'")
        
        print("\n[ Create or Edit ]")
        # <<< --- MENU UPDATED --- >>>
        create_option = len(scenario_keys) + 1 # Now 5 + 1 = 6
        all_option = len(scenario_keys) + 2    # 7
        edit_option = len(scenario_keys) + 3   # 8
        buffer_option = len(scenario_keys) + 4 # 9
        exit_option = len(scenario_keys) + 5   # 10
        print(f"  {create_option}: Create New Mission & Run vs. Existing Scenario")
        print(f"  {all_option}: Run ALL Scenarios from config.json (Default Times)")
        print(f"  {edit_option}: How to Edit/Save Missions (in config.json)")
        print(f"  {buffer_option}: Change Safety Buffers")
        print(f"  {exit_option}: Exit")
        print("===" * 20)
        print(f"CURRENT SETTINGS: Buffers (H={SAFETY_BUFFER_HORIZONTAL}m, V={SAFETY_BUFFER_VERTICAL}m)")
        # <<< --- END OF MENU UPDATE --- >>>

        
        try:
            choice_input = input(f"Enter choice (1-{exit_option}): ")
            choice_index = int(choice_input)
        except ValueError:
            print("\nInvalid input. Please enter a number.")
            continue 

        # Option: Exit
        if choice_index == exit_option:
            print("\nExiting deconfliction tool. Goodbye!")
            break 
        
        # Option: Change Buffers
        elif choice_index == buffer_option:
            change_safety_buffers()
            continue

        # Option: How to Edit
        elif choice_index == edit_option:
            print("\n" + "---" * 20)
            print("   HOW TO EDIT/SAVE MISSIONS")
            print("---" * 20)
            print(f"This tool runs scenarios from the '{CONFIG_FILE}' file.")
            print("To permanently edit speeds, waypoints, or add/remove drones,")
            print(f"please close this tool and open '{CONFIG_FILE}' in a text editor.")
            print("\nUse Option 6 ('Create New Mission') to test temporary missions.")
            print("---" * 20)
            print("\nPress Enter to return to the main menu.")
            input()
            continue 

        # Option: Run All
        elif choice_index == all_option:
            print("\n" + "---" * 20)
            print("🚀 RUNNING ALL SCENARIOS (DEFAULT TIMES)")
            print("---" * 20)
            for key in scenario_keys:
                scenario = all_scenarios[key]
                default_start_time = scenario["primary_mission"].mission_start_time
                run_simulation(
                    scenario_name=scenario["scenario_name"],
                    primary_mission=scenario["primary_mission"],
                    simulated_flights=scenario["simulated_flights"],
                    desired_start_time=default_start_time,
                    create_animation=True 
                )
            print("\nAll scenarios complete.")
            print("Press Enter to return to main menu.")
            input()
            continue
        
        # Option: Create New Mission Wizard
        elif choice_index == create_option:
            print("\n" + "---" * 10)
            print("   CREATE & RUN WIZARD")
            print("---" * 10)
            print("First, which simulated airspace do you want to test against?")
            for i, key in enumerate(scenario_keys):
                print(f"  {i+1}: Use drones from '{all_scenarios[key]['scenario_name']}'")
            
            chosen_sim_scenario = None
            while True:
                try:
                    sim_choice_input = input(f"Enter choice (1-{len(scenario_keys)}): ")
                    sim_choice_index = int(sim_choice_input) - 1
                    if 0 <= sim_choice_index < len(scenario_keys):
                        chosen_sim_key = scenario_keys[sim_choice_index]
                        chosen_sim_scenario = all_scenarios[chosen_sim_key]
                        break
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            
            new_primary_mission = create_mission_wizard()
            if new_primary_mission is None:
                print("Mission creation failed. Returning to main menu.")
                continue

            print("\nNew mission created.")
            print(f"  Allowed window: t={new_primary_mission.mission_start_time}s to t={new_primary_mission.mission_end_time}s.")
            while True:
                try:
                    start_time_input = input("Enter desired start time for this new mission: ")
                    desired_start_time = float(start_time_input)
                    break
                except ValueError:
                    print("Invalid input. Please enter a number.")

            run_simulation(
                scenario_name="Custom Mission vs. " + chosen_sim_scenario['scenario_name'],
                primary_mission=new_primary_mission,
                simulated_flights=chosen_sim_scenario["simulated_flights"],
                desired_start_time=desired_start_time,
                create_animation=True
            )
            
            print("Simulation complete. Press Enter to return to main menu.")
            input() 
            continue

        # Option: Run a Single Scenario (from config)
        elif 1 <= choice_index <= len(scenario_keys):
            chosen_key = scenario_keys[choice_index - 1]
            chosen_scenario = all_scenarios[chosen_key]
            
            print(f"\n--- SCENARIO: {chosen_scenario['scenario_name']} ---")
            pm = chosen_scenario['primary_mission']
            
            wp1, wp2 = pm.waypoints[0], pm.waypoints[-1]
            dist = math.sqrt((wp1.x - wp2.x)**2 + (wp1.y - wp2.y)**2 + (wp1.z - wp2.z)**2)
            duration = dist / pm.speed
            
            print(f"  Primary mission takes ~{duration:.1f}s to fly.")
            print(f"  Allowed mission window: t={pm.mission_start_time}s to t={pm.mission_end_time}s.")
            
            for sim_drone in chosen_scenario['simulated_flights']:
                print(f"  Conflicting drone '{sim_drone.flight_id}' flies from t={sim_drone.trajectory[0].time}s to t={sim_drone.trajectory[-1].time}s.")
            
            while True:
                try:
                    start_time_input = input("\nEnter desired start time (e.g., '0.0', '10.1'): ")
                    desired_start_time = float(start_time_input)
                    break
                except ValueError:
                    print("Invalid input. Please enter a number.")

            run_simulation(
                scenario_name=chosen_scenario["scenario_name"],
                primary_mission=chosen_scenario["primary_mission"],
                simulated_flights=chosen_scenario["simulated_flights"],
                desired_start_time=desired_start_time,
                create_animation=True
            )
            
            print("Simulation complete. Press Enter to return to main menu.")
            input() 
            continue 
        
        else:
            print("\nInvalid choice. Please enter a number from the list.")
            continue