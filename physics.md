# GT Racing Line Simulator — Physics & Features

## Project Overview

This project simulates the ideal racing line for GT race cars using linear algebra and physics-based modeling. The racing line is represented as a vector of track positions, optimized using matrix operations to find the smoothest and fastest path through any circuit.

---

## Features

| Feature | Description |
|---|---|
| Aerodynamics | Models downforce and drag effect on cornering speed |
| Tyre Grip | Grip limit determines how fast the car can take a corner |
| Lateral G-Force | Caps the maximum sideways acceleration on the racing line |
| Suspension | Smooths out the car's response over bumps and track camber |
| Track Elevation | Accounts for uphill/downhill sections affecting braking and acceleration |
| Braking Zones | Calculates where the car must begin braking before corners |
| Track Boundaries | Inner and outer walls define the space the racing line must stay within |
| Racing Line Optimization | Uses matrix operations to find the smoothest, fastest path through the track |

---

## Physics

### 1. Aerodynamics

Downforce increases with the square of speed:

$$F_{down} = \frac{1}{2} \rho v^2 C_L A$$

Drag opposes the car's motion:

$$F_{drag} = \frac{1}{2} \rho v^2 C_D A$$

**Terms:**
- **F_down** — Downforce; the force pushing the car down onto the track (Newtons)
- **F_drag** — Drag force; air resistance opposing the car's motion (Newtons)
- **ρ (rho)** — Air density; how "thick" the air is (kg/m³), typically 1.225 at sea level
- **v** — Speed of the car (m/s)
- **v²** — Speed squared; aero forces grow very fast as speed increases
- **C_L** — Lift coefficient; how effectively the car generates downforce (dimensionless)
- **C_D** — Drag coefficient; how much air resistance the car creates (dimensionless)
- **A** — Reference area; typically the car's frontal area (m²)

---

### 2. Tyre Grip

Maximum lateral force a tyre can produce before sliding:

$$F_{lat} = \mu \cdot N$$

**Terms:**
- **F_lat** — Maximum lateral (sideways) force the tyre can handle before losing grip (Newtons)
- **μ (mu)** — Friction coefficient; how grippy the tyre is (0 = ice, ~1.5 for racing slicks)
- **N** — Normal force; the force pushing the tyre into the ground (weight + downforce)

---

### 3. Lateral G-Force

Centripetal acceleration needed to follow a curved path:

$$a_{lat} = \frac{v^2}{r}$$

The car must always satisfy:

$$a_{lat} \leq \mu g$$

**Terms:**
- **a_lat** — Lateral acceleration; how strongly the car is pushed sideways in a corner (m/s²)
- **v²** — Speed squared
- **r** — Radius of the corner (m); bigger radius = gentler corner = higher speed possible
- **μ** — Friction coefficient (same as tyre grip)
- **g** — Gravitational acceleration (9.81 m/s²)
- The condition **a_lat ≤ μg** means sideways force cannot exceed what the tyres can handle

---

### 4. Suspension

Simple spring-damper model for vertical car motion:

$$m\ddot{x} + c\dot{x} + kx = F_{road}$$

For a full car (4 corners), this becomes a matrix system of equations.

**Terms:**
- **m** — Mass of the car (kg)
- **x** — Vertical displacement; how much the suspension moves up/down (m)
- **ẋ (x dot)** — Velocity of suspension movement; first derivative of x (m/s)
- **ẍ (x double dot)** — Acceleration of suspension movement; second derivative of x (m/s²)
- **c** — Damping coefficient; how much the shock absorber resists movement (higher = stiffer damper)
- **k** — Spring stiffness; how hard the spring pushes back (higher = stiffer ride)
- **F_road** — Force input from the road surface (bumps, elevation changes)

---

### 5. Track Elevation

On a slope of angle θ, the net driving force changes:

$$F_{net} = F_{drive} - mg\sin\theta - F_{drag}$$

**Terms:**
- **F_net** — Net force actually accelerating the car forward (Newtons)
- **F_drive** — Engine driving force (Newtons)
- **m** — Car mass (kg)
- **g** — Gravity (9.81 m/s²)
- **θ (theta)** — Angle of the slope (degrees or radians)
- **sin(θ)** — The steeper the hill, the more gravity works against the car
- **F_drag** — Air resistance pulling the car back (Newtons)

---

### 6. Braking Zones

Maximum deceleration under braking on a slope:

$$a_{brake} = \mu g \cos\theta$$

Minimum braking distance from speed v:

$$d = \frac{v^2}{2 \cdot a_{brake}}$$

**Terms:**
- **a_brake** — Maximum deceleration the car can achieve (m/s²)
- **μ** — Tyre friction coefficient
- **g** — Gravity (9.81 m/s²)
- **cos(θ)** — On a slope, braking grip is slightly reduced; cos accounts for the angle
- **d** — Braking distance needed to slow down from speed v (m)
- **v²** — Speed squared; double the speed = 4× the braking distance

---

### 7. Racing Line Optimization (Core Linear Algebra)

The racing line is represented as a vector **α** of values between 0 and 1:

$$\alpha = [\alpha_1, \alpha_2, \alpha_3, \ldots, \alpha_n]^T$$

Where each αᵢ = 0 means the car is at the inner wall, and αᵢ = 1 means the car is at the outer wall.

We minimize curvature (find the smoothest path) by solving:

$$\min_{\alpha} \quad \alpha^T Q \alpha$$

Where **Q** is a tridiagonal matrix:

$$Q = \begin{bmatrix} 2 & -1 & 0 & \cdots \\ -1 & 2 & -1 & \cdots \\ 0 & -1 & 2 & \cdots \\ \vdots & & & \ddots \end{bmatrix}$$

**Terms:**
- **α (alpha)** — Vector of track position values at each point along the track (between 0 and 1)
- **αᵀ** — Transpose of alpha; flips it from a column vector to a row vector
- **Q** — Tridiagonal matrix; penalizes sharp direction changes, enforcing a smooth path
- **αᵀQα** — A single number representing how "rough" the path is; minimizing it finds the smoothest racing line
- **n** — Number of track sample points

---

## How It All Connects

```
Track Boundaries (inner/outer walls)
        ↓
α vector (position across track at each point)
        ↓
Apply constraints:
  - Lateral G ≤ μg  (grip limit from tyres + aero downforce)
  - Braking distance (elevation + friction)
  - Suspension smoothing (road input forces)
        ↓
Minimize αᵀQα  (smoothest path = fastest racing line)
        ↓
Optimal Racing Line
```

---



Segment i:
├── position
│   ├── α_i          (where across track, 0 to 1)
│   ├── x_i, y_i     (actual coordinates on track)
│   └── elevation_i  (height at this point)
│
├── geometry
│   ├── r_i          (corner radius)
│   ├── θ_i          (slope angle, uphill/downhill)
│   └── φ_i          (heading angle, direction car is facing)
│
├── velocity
│   ├── v_entry_i    (speed entering this segment)
│   └── v_exit_i     (speed leaving this segment)
│
└── forces
    ├── F_down_i     (downforce at this speed)
    ├── F_drag_i     (drag at this speed)
    ├── F_lat_i      (lateral grip limit)
    └── a_brake_i    (max braking decel)