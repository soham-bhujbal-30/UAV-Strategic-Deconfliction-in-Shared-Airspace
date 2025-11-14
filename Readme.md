# UAV Strategic Deconfliction System

A **4D (3D space + time) deconfliction system** for drone missions operating in shared airspace. Built as a technical assessment for **FlytBase**, this system analyzes proposed drone missions to ensure strategic safety before launch.

---

## 🚀 Overview
The system acts as a **central authority** that verifies whether a drone's planned mission can be safely executed. It compares the mission against a dataset of other drones' flight schedules, detecting any **space-time conflicts**.

---

## ✨ Core Features
### **🔍 True 4D Conflict Detection**
- Compares drone trajectories in **3D space (x, y, z)** over **time (t)**.
- Checks for positional overlap at discrete timestamps.

### **🖥️ Interactive Command-Line Interface**
- Run `main.py` to choose a scenario and start time.
- Easily test various parameters.

### **🛫 Strategic Deconfliction**
- Helps users find a **safe start time** for missions that initially conflict.

### **🗂️ Configurable Scenarios**
- All missions and drone parameters are stored in `config.json`.
- Modify speeds, routes, drones, or add new scenarios.

### **📽️ 3D/4D Visualization**
- Automatically generates an `.mp4` animation of each simulation.
- Conflict points are marked with a **red X** for clarity.

---

## 📁 Project Structure
```
/
├── main.py                   # Interactive CLI tool
├── config.json               # Edit all missions & scenarios here
├── conflict_checker.py       # Core 4D conflict detection engine
├── visualization.py          # 3D/4D animation generator
├── data_models.py            # Dataclasses for all objects
└── test_conflict_checker.py  # Pytest unit tests
```

---

## 🔧 Setup & Installation
### 1. **Clone or Download the Repository**
```
# Example
git clone <repo-url>
cd <folder>
```

### 2. **Install Python Dependencies**
```
pip install matplotlib
pip install pytest
pip install pillow
```

### 3. **Install ffmpeg** (Required for `.mp4` video generation)
- **Windows:** `choco install ffmpeg`
- **Mac:** `brew install ffmpeg`
- **Linux:** `sudo apt-get install ffmpeg`

> If `ffmpeg` is not installed, the script will fallback to generating `.gif` animations using Pillow.

---

## ▶️ How to Use
This project provides an **interactive CLI tool** via `main.py`.

### **1. Configure Missions (Optional)**
Open `config.json`:
- Adjust drone speeds
- Add/remove waypoints (x, y, z)
- Add new simulated drones
- Create new scenarios

### **2. Run the Tool**
```
python main.py
```

### **3. Use the Interactive Menu**
You will be prompted:

#### **(a) Choose a scenario**
Example options:
- Clear Scenario
- Head-On Conflict
- 3D Near Miss

#### **(b) Enter desired start time**
Example:
- Enter `0.0` → may cause CONFLICT
- Enter `10.1` → may become CLEAR

This lets you explore safe start windows.

---

## 📤 Output
### **Terminal Output**
- Detailed conflict evaluation
- Example: `STATUS: CLEAR` or `CONFLICT DETECTED`

### **Generated Files**
- A 3D animation for each simulation
- Filename example:
```
simulation_head-on_conflict_t_start_10.1.mp4
```

---

## 🧪 Running Tests
To verify correctness:
```
python -m pytest -v
```
You should see all tests pass.

---

## 📌 Notes
- Designed for simulation/testing, not real-world traffic management.
- Highly extensible due to the JSON-based scenario configuration.

---

## 📄 License
MIT License (or specify your own here).

---

## 🙌 Acknowledgments
Built for FlytBase as part of a technical assessment.

