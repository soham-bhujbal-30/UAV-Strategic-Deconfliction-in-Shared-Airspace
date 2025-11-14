import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Optional
from data_models import (
    SimulatedFlight, 
    ConflictReport, 
    Waypoint,
    TimedWaypoint
)
from conflict_checker import _find_drone_position # Import helper

# --- CONFIGURATION ---
TIME_STEP = 0.5
DEFAULT_VIDEO_FILENAME = "simulation.gif"

def plot_full_trajectory(ax, trajectory: List[TimedWaypoint], style: str = ':', color: str = 'grey'):
    """Helper to plot the complete 3D path of a single drone."""
    if not trajectory:
        return
    x_coords = [wp.x for wp in trajectory]
    y_coords = [wp.y for wp in trajectory]
    z_coords = [wp.z for wp in trajectory]
    ax.plot(x_coords, y_coords, z_coords, linestyle=style, color=color, alpha=0.5)

def animate_simulation(
    primary_trajectory: List[TimedWaypoint], # <<< Pass in trajectory
    simulated_flights: List[SimulatedFlight],
    conflict_report: ConflictReport,
    scenario_name: str = "Simulation",
    output_filename: Optional[str] = None
):
    """
    Generates and saves a 3D animation of the drone simulation.
    """
    print(f"\n🎥 Generating 3D animation for: {scenario_name}...")

    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # --- 2. Calculate Bounds ---
    all_trajectories = [primary_trajectory] + [f.trajectory for f in simulated_flights]
    valid_trajectories = [traj for traj in all_trajectories if traj]
    
    if not valid_trajectories:
        print("No trajectories to animate.")
        plt.close(fig)
        return

    all_times = [wp.time for traj in valid_trajectories for wp in traj]
    if not all_times:
        print("No waypoints with time to animate.")
        plt.close(fig)
        return
        
    t_min = min(all_times)
    t_max = max(all_times)
    total_duration = t_max - t_min
    
    if total_duration <= 0:
        num_frames = 1
    else:
        num_frames = int(total_duration / TIME_STEP)
        if num_frames == 0:
             num_frames = 1
    
    all_x = [wp.x for traj in valid_trajectories for wp in traj]
    all_y = [wp.y for traj in valid_trajectories for wp in traj]
    all_z = [wp.z for traj in valid_trajectories for wp in traj]
    
    if not all_x or not all_y or not all_z:
        print("No 3D spatial data to animate.")
        plt.close(fig)
        return
        
    x_min, x_max = min(all_x) - 10, max(all_x) + 10
    y_min, y_max = min(all_y) - 10, max(all_y) + 10
    z_min, z_max = min(all_z) - 10, max(all_z) + 10
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)
    
    ax.view_init(elev=20., azim=-65) 
    
    ax.set_title(f"UAV Deconfliction (3D View): {scenario_name}")
    ax.set_xlabel("X Coordinate (meters)")
    ax.set_ylabel("Y Coordinate (meters)")
    ax.set_zlabel("Altitude (meters)")

    # --- 3. Plot Static Elements ---
    plot_full_trajectory(ax, primary_trajectory, style='--', color='blue')
    for sim_flight in simulated_flights:
        plot_full_trajectory(ax, sim_flight.trajectory, style=':', color='green')

    if conflict_report.status == "CONFLICT_DETECTED":
        for conflict in conflict_report.conflicts:
            if "MISSION_TIME_WINDOW" not in conflict.conflicted_with_flight_id:
                ax.scatter(
                    conflict.location.x, 
                    conflict.location.y, 
                    conflict.location.z,
                    c='red', marker='X', s=200,
                    label=f"Conflict at t={conflict.time}s"
                )

    # --- 4. Initialize Animated Elements ---
    primary_dot, = ax.plot([], [], [], 'bo', markersize=10, label="Primary Drone")
    sim_dots = []
    for i, sim_flight in enumerate(simulated_flights):
        dot, = ax.plot(
            [], [], [], 'go', markersize=8, 
            label=f"{sim_flight.flight_id}"
        )
        sim_dots.append(dot)
        
    time_text = ax.text2D(0.02, 0.95, '', transform=ax.transAxes)
    
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='upper right')

    # --- 5. Define Animation Functions ---
    def init():
        primary_dot.set_data_3d([], [], [])
        for dot in sim_dots:
            dot.set_data_3d([], [], [])
        time_text.set_text('')
        return [primary_dot, *sim_dots, time_text]

    def update(frame):
        current_time = t_min + (frame * TIME_STEP)
        
        primary_pos = _find_drone_position(primary_trajectory, current_time)
        if primary_pos:
            primary_dot.set_data_3d(
                [primary_pos.x], [primary_pos.y], [primary_pos.z]
            )
        else:
            primary_dot.set_data_3d([], [], [])
            
        for i, sim_flight in enumerate(simulated_flights):
            sim_pos = _find_drone_position(sim_flight.trajectory, current_time)
            if sim_pos:
                sim_dots[i].set_data_3d(
                    [sim_pos.x], [sim_pos.y], [sim_pos.z]
                )
            else:
                sim_dots[i].set_data_3d([], [], [])
        
        time_text.set_text(f'Time: {current_time:.1f}s')
        
        return [primary_dot, *sim_dots, time_text]

    # --- 6. Create and Save Animation ---
    ani = FuncAnimation(
        fig, 
        update, 
        frames=num_frames + 1, # Includes the animation fix
        init_func=init, 
        blit=False, 
        interval=50
    )
    
    try:
        if output_filename is None:
            output_filename = DEFAULT_VIDEO_FILENAME
        
        # Save as MP4 since your ffmpeg is working
        if output_filename.endswith('.mp4'):
            print(f"Saving animation as MP4 (using 'ffmpeg' writer)...")
            ani.save(output_filename, writer='ffmpeg', fps=20)
            print(f"✅ Animation saved successfully as '{output_filename}'")
        else:
            # Fallback for GIF
            print(f"Saving animation as GIF (using 'pillow' writer)...")
            writer = PillowWriter(fps=10)
            ani.save(output_filename, writer=writer)
            print(f"✅ Animation saved successfully as '{output_filename}'")

    except Exception as e:
        print(f"--- ⚠️ ANIMATION FAILED TO SAVE ---")
        print(f"Error: {e}")
        print("Please ensure 'pillow' and/or 'ffmpeg' are installed.")
        
    plt.close(fig)