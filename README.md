# GT Racing Line Simulator

> Streamlit app that computes the optimal racing line for GT circuits using quadratic optimization and physics-based constraints — with real-time animated convergence.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red) ![NumPy](https://img.shields.io/badge/NumPy-linear--algebra-orange) ![Plotly](https://img.shields.io/badge/Plotly-visualization-green)

---

## What It Does

Given a circuit layout (inner wall, outer wall, center line), the simulator finds the smoothest and fastest path through the track by solving a constrained quadratic optimization problem.

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

*Made as a math/physics project at PES University.*
