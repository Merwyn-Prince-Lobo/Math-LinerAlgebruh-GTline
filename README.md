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

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/yourname/gt-racing-line-simulator
cd gt-racing-line-simulator
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> If `requirements.txt` is missing:
```bash
pip install streamlit numpy scipy plotly
```

### 4. Launch the app
```bash
streamlit run app.py
```

### 5. Open in browser
http://localhost:8501

---

## ⚠️ Notes
- Requires Python 3.8+
- Activate virtual environment before running
- Install missing modules if errors occur

---

## Track CSV Format

The uploader accepts CSVs with this column structure:

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

1. **α vector** initialized at 0.5  
2. **Q matrix** built as a tridiagonal Laplacian  
3. Gradient:
   - Smoothness: `∇ = 2Qα`
   - Apex targeting included  
4. Update step with clipping  
5. Iterate and render live  

---

## Project Structure

```
gt-racing-line-simulator/
├── app.py
├── Monza.csv
├── requirements.txt
├── physics.md
├── features.md
└── README.md
```

---

## Built With

- Streamlit  
- NumPy  
- SciPy  
- Plotly  

---

*Made as a math/physics project at PES University — linear algebra applied to motorsport.*
