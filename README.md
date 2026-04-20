# GT Racing Line Simulator

> Streamlit app that computes the optimal racing line for GT circuits using quadratic optimization and physics-based constraints — with real-time animated convergence.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red) ![NumPy](https://img.shields.io/badge/NumPy-linear--algebra-orange) ![Plotly](https://img.shields.io/badge/Plotly-visualization-green)

---

## What It Does

Given a circuit layout (inner wall, outer wall, center line), the simulator finds the smoothest and fastest path through the track by solving a constrained quadratic optimization problem. The racing line is represented as a vector **α** of track-position values (0 = inner wall, 1 = outer wall), and the optimizer minimizes:

$$\min_{\alpha} \quad \alpha^T Q \alpha$$

where **Q** is a tridiagonal smoothness matrix, subject to physics constraints from tyre grip, aerodynamic downforce, and lateral G-force limits.

---

## Features

- **Real track CSV support** — drop any circuit CSV (`x_m, y_m, w_tr_right_m, w_tr_left_m`) and run instantly
- **Ghost line animation** — watch previous iterations fade out as the optimizer converges in real-time
- **Physics modeling** — aero downforce/drag, tyre friction, lateral G-force, braking zones, track elevation
- **Speed profile** — per-segment velocity computed from grip limits and corner radius
- **Convergence plot** — cost history `αᵀQα` across iterations
- **Tunable parameters** — downforce (CL), drag (CD), friction (μ), spring stiffness, damping, learning rate
- **Preset tracks** — Monza (real data), Spa-Francorchamps, Suzuka, Silverstone

---

## Physics Overview

| Model | Formula |
|---|---|
| Downforce | `F_down = ½ρv²C_L·A` |
| Drag | `F_drag = ½ρv²C_D·A` |
| Max lateral force | `F_lat = μ·N` |
| Cornering limit | `a_lat = v²/r ≤ μg` |
| Braking distance | `d = v² / (2μg·cosθ)` |
| Suspension | `mẍ + cẋ + kx = F_road` |

---

## Installation

```bash
git clone https://github.com/yourname/gt-racing-line-simulator
cd gt-racing-line-simulator
pip install -r requirements.txt
streamlit run app.py
```

**Requirements:**
```
streamlit
numpy
scipy
plotly
```

---

## Track CSV Format

The uploader accepts CSVs with this column structure (same format as the [TUM Motorsport dataset](https://github.com/TUMFTM/racetrack-database)):

```
# x_m,y_m,w_tr_right_m,w_tr_left_m
-0.32, 1.09, 5.74, 5.93
0.17,  6.06, 5.73, 5.93
...
```

- `x_m`, `y_m` — center line coordinates in meters
- `w_tr_right_m` — track width to the right wall
- `w_tr_left_m` — track width to the left wall

---

## How the Optimizer Works

1. **α vector** initialized at 0.5 (center of track) for each segment
2. **Q matrix** built as a tridiagonal Laplacian — penalizes direction changes between adjacent segments
3. Each iteration computes a combined gradient:
   - **Smoothness:** `∇_smooth = 2Qα` — pulls the line toward uniform curvature
   - **Apex targeting:** `∇_apex = w·(α - α_target)` — weighted by track curvature, pushes the line to the inside of corners
4. `α ← α - lr·∇` then clipped to `[0.05, 0.95]` to stay within walls
5. Repeats for N iterations, rendering each step live

---

## Project Structure

```
gt-racing-line-simulator/
├── app.py            # Main Streamlit app
├── Monza.csv         # Real Monza circuit data
├── requirements.txt
├── physics.md        # Physics derivations and equations
├── features.md       # Feature list
└── README.md
```

---

## Built With

- [Streamlit](https://streamlit.io) — UI and live rendering
- [NumPy](https://numpy.org) — matrix math, Q matrix, gradient computation
- [Plotly](https://plotly.com) — interactive track and telemetry plots
- [Monza CSV data](https://github.com/TUMFTM/racetrack-database) — TUM Motorsport open racetrack dataset

---
How to Run
1. Clone the repository
git clone <your-repo-link>
cd Math-LinerAlgebruh-GTline
2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt

If requirements.txt is not available:

pip install streamlit numpy scipy plotly
4. Run the app
streamlit run app.py
5. Open in browser

After running, the app will be available at:
http://localhost:8501
⚠️ Notes
Make sure Python 3.8+ is installed
Always activate the virtual environment before running
If you get module errors, install missing packages using pip install <module>
*Made as a math/physics project at PES University — linear algebra applied to motorsport.*
