import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter # <<< CRITICAL FIX: Import PillowWriter
from mpl_toolkits.mplot3d import Axes3D # <<< 3D IMPORT
from typing import List, Optional
from data_models import (
    PrimaryMission, 
    SimulatedFlight, 
    ConflictReport, 
    Waypoint,
    TimedWaypoint
)
from conflict_checker import (
    _convert_mission_to_trajectory, 
    _find_drone_position,
    interpolate_position
)

# --- CONFIGURATION ---
TIME_STEP = 0.5 # Must match the time_step in main.py for accuracy
DEFAULT_VIDEO_FILENAME = "simulation.gif" # Default to GIF

def plot_full_trajectory(ax, trajectory: List[TimedWaypoint], style: str = ':', color: str = 'grey'):
    """Helper to plot the complete 3D path of a single drone."""
    if not trajectory:
        return
    x_coords = [wp.x for wp in trajectory]
    y_coords = [wp.y for wp in trajectory]
    z_coords = [wp.z for wp in trajectory] # <<< 3D UPDATE
    # <<< 3D UPDATE >>>
    ax.plot(x_coords, y_coords, z_coords, linestyle=style, color=color, alpha=0.5)

def animate_simulation(
    primary_mission: PrimaryMission,
    simulated_flights: List[SimulatedFlight],
    conflict_report: ConflictReport,
    scenario_name: str = "Simulation",
    output_filename: Optional[str] = None
):
    """
    Generates and saves a 3D animation of the drone simulation.
    """
    print(f"\n🎥 Generating 3D animation for: {scenario_name}...")

    # --- 1. Setup Figure and Axis ---
    # <<< 3D UPDATE >>>
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # --- 2. Calculate Primary Trajectory & Time Bounds ---
    try:
        primary_trajectory = _convert_mission_to_trajectory(primary_mission)
    except ValueError:
        print("Error: Cannot animate mission with invalid parameters.")
        plt.close(fig)
        return

    all_trajectories = [primary_trajectory] + [f.trajectory for f in simulated_flights]
    
    # Filter out any None or empty trajectories
    valid_trajectories = [traj for traj in all_trajectories if traj]
    
    if not valid_trajectories:
        print("No trajectories to animate.")
        plt.close(fig)
        return

    # Find global time bounds
    all_times = [wp.time for traj in valid_trajectories for wp in traj]
    if not all_times:
        print("No waypoints with time to animate.")
        plt.close(fig)
        return
        
    t_min = min(all_times)
    t_max = max(all_times)
    total_duration = t_max - t_min
    
    # Handle zero duration
    if total_duration <= 0:
        num_frames = 1
    else:
        num_frames = int(total_duration / TIME_STEP)
        if num_frames == 0:
             num_frames = 1
    
    # Find global spatial bounds
    all_x = [wp.x for traj in valid_trajectories for wp in traj]
    all_y = [wp.y for traj in valid_trajectories for wp in traj]
    all_z = [wp.z for traj in valid_trajectories for wp in traj] # <<< 3D UPDATE
    
    # Handle cases with no spatial data
    if not all_x or not all_y or not all_z:
        print("No 3D spatial data to animate.")
        plt.close(fig)
        return
        
    x_min, x_max = min(all_x) - 10, max(all_x) + 10 # Add 10-unit buffer
    y_min, y_max = min(all_y) - 10, max(all_y) + 10
    z_min, z_max = min(all_z) - 10, max(all_z) + 10 # <<< 3D UPDATE
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max) # <<< 3D UPDATE
    
    # Set a good viewing angle
    ax.view_init(elev=20., azim=-65) 
    
    ax.set_title(f"UAV Deconfliction (3D View): {scenario_name}")
    ax.set_xlabel("X Coordinate (meters)")
    ax.set_ylabel("Y Coordinate (meters)")
    ax.set_zlabel("Altitude (meters)") # <<< 3D UPDATE

    # --- 3. Plot Static Elements ---
    
    # Plot full paths
    plot_full_trajectory(ax, primary_trajectory, style='--', color='blue')
    for sim_flight in simulated_flights:
        plot_full_trajectory(ax, sim_flight.trajectory, style=':', color='green')

    # Plot conflict points
    if conflict_report.status == "CONFLICT DETECTED":
        for conflict in conflict_report.conflicts:
            # Avoid plotting mission time window errors
            if "MISSION_TIME_WINDOW" not in conflict.conflicted_with_flight_id:
                # <<< 3D UPDATE (use scatter for 3D points) >>>
                ax.scatter(
                    conflict.location.x, 
                    conflict.location.y, 
                    conflict.location.z,
                    c='red',
                    marker='X', 
                    s=200, # Large size
                    label=f"Conflict at t={conflict.time}s"
                )

    # --- 4. Initialize Animated Elements ---
    
    # Primary drone dot
    # <<< 3D UPDATE (add z dimension) >>>
    primary_dot, = ax.plot([], [], [], 'bo', markersize=10, label="Primary Drone")
    
    # Simulated drone dots
    sim_dots = []
    for i, sim_flight in enumerate(simulated_flights):
        # <<< 3D UPDATE (add z dimension) >>>
        dot, = ax.plot(
            [], [], [], 'go', markersize=8, 
            label=f"{sim_flight.flight_id}"
        )
        sim_dots.append(dot)
        
    # Time text
    time_text = ax.text2D(0.02, 0.95, '', transform=ax.transAxes) # text2D for 3D plots
    
    # Handle duplicate labels in legend
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right')

    # --- 5. Define Animation Functions ---
    
    def init():
        """Initializes the animation frame."""
        # <<< 3D UPDATE (use set_data_3d) >>>
        primary_dot.set_data_3d([], [], [])
        for dot in sim_dots:
            dot.set_data_3d([], [], [])
        time_text.set_text('')
        return [primary_dot, *sim_dots, time_text]

    def update(frame):
        """Called for each frame of the animation."""
        current_time = t_min + (frame * TIME_STEP)
        
        # Update primary drone
        primary_pos = _find_drone_position(primary_trajectory, current_time)
        if primary_pos:
            # <<< 3D UPDATE (use set_data_3d) >>>
            primary_dot.set_data_3d(
                [primary_pos.x], [primary_pos.y], [primary_pos.z]
            )
        else:
            primary_dot.set_data_3d([], [], []) # Hide dot if not in flight
            
        # Update simulated drones
        for i, sim_flight in enumerate(simulated_flights):
            sim_pos = _find_drone_position(sim_flight.trajectory, current_time)
            if sim_pos:
                # <<< 3D UPDATE (use set_data_3d) >>>
                sim_dots[i].set_data_3d(
                    [sim_pos.x], [sim_pos.y], [sim_pos.z]
                )
            else:
                sim_dots[i].set_data_3d([], [], []) # Hide dot
        
        time_text.set_text(f'Time: {current_time:.1f}s')
        
        return [primary_dot, *sim_dots, time_text]

    # --- 6. Create and Save Animation ---
    
    ani = FuncAnimation(
        fig, 
        update, 
        frames=num_frames, 
        init_func=init, 
        blit=False, # <<< 3D UPDATE (blit=True is not supported in mplot3d)
        interval=50 # 50ms between frames
    )
    
    # <<< CRITICAL FIX: Use the explicit PillowWriter >>>
    try:
        if output_filename is None:
            output_filename = DEFAULT_VIDEO_FILENAME

        if output_filename.endswith('.gif'):
            print(f"Saving animation as GIF (using 'pillow' writer)...")
            writer = PillowWriter(fps=10) # Use the explicit class
            ani.save(output_filename, writer=writer)
            print(f"✅ Animation saved successfully as '{output_filename}'")
        
        elif output_filename.endswith('.mp4'):
            print(f"Saving animation as MP4 (using 'ffmpeg' writer)...")
            ani.save(output_filename, writer='ffmpeg', fps=20)
            print(f"✅ Animation saved successfully as '{output_filename}'")
        
        else:
            print(f"--- ⚠️ ANIMATION FAILED TO SAVE ---")
            print(f"Error: Unknown file extension. Please use .gif or .mp4")

    except Exception as e:
        print(f"--- ⚠️ ANIMATION FAILED TO SAVE ---")
        print(f"Error: {e}")
        print("Please ensure 'pillow' is installed (`pip install pillow`)")
        if output_filename.endswith('.mp4'):
             print("If saving .mp4, ensure 'ffmpeg' is installed and in your system's PATH.")
        
    plt.close(fig) # Close the figure to free up memory