Features

Aerodynamics — models downforce and drag effect on cornering speed
Tyre Grip — grip limit determines how fast the car can take a corner
Lateral G-Force — caps the maximum sideways acceleration on the racing line
Suspension — smooths out the car's response over bumps and track camber
Track Elevation — accounts for uphill/downhill sections affecting braking and acceleration
Braking Zones — calculates where the car must begin braking before corners
Track Boundaries — inner and outer walls define the space the racing line must stay within
Racing Line Optimization — uses matrix operations to find the smoothest, fastest path through the track




// web stack dev 
Streamlit (UI + visualization)
    ↓
NumPy (matrix math, Q matrix, segment data)
    ↓
SciPy (optimization solver)
    ↓
Matplotlib / Plotly (track + racing line animation)