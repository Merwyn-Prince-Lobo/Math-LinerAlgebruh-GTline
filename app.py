import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GT Racing Line Simulator",
    page_icon="🏎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background-color: #0a0a0f;
    color: #e0e0e0;
}

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0f0f1a 50%, #0a0a0f 100%);
}

h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 2px;
}

.main-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.4rem;
    font-weight: 900;
    background: linear-gradient(90deg, #ff4444, #ff8800, #ffcc00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 4px;
    text-align: center;
    margin-bottom: 0.2rem;
}

.subtitle {
    text-align: center;
    color: #888;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

.metric-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid #ff440033;
    border-left: 3px solid #ff4444;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin: 0.4rem 0;
}

.metric-label {
    font-size: 0.7rem;
    color: #888;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.metric-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #ff8800;
}

.metric-unit {
    font-size: 0.8rem;
    color: #666;
    margin-left: 4px;
}

.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'Orbitron', monospace;
    letter-spacing: 1px;
}

.status-ready {
    background: #1a3a1a;
    border: 1px solid #44ff44;
    color: #44ff44;
}

.status-running {
    background: #3a2a00;
    border: 1px solid #ff8800;
    color: #ff8800;
}

.sidebar-header {
    font-family: 'Orbitron', monospace;
    font-size: 0.75rem;
    color: #ff4444;
    letter-spacing: 3px;
    text-transform: uppercase;
    border-bottom: 1px solid #ff444433;
    padding-bottom: 6px;
    margin-bottom: 12px;
    margin-top: 20px;
}

div[data-testid="stSlider"] label {
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 1px;
    color: #aaa !important;
}

div[data-testid="stSelectbox"] label {
    font-family: 'Rajdhani', sans-serif !important;
    letter-spacing: 1px;
    color: #aaa !important;
}

.stButton > button {
    background: linear-gradient(90deg, #ff4444, #ff8800) !important;
    color: white !important;
    font-family: 'Orbitron', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.6rem 2rem !important;
    font-size: 0.85rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
}

.iter-text {
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    color: #ff8800;
    letter-spacing: 2px;
    text-align: center;
}

.section-divider {
    border: none;
    border-top: 1px solid #ffffff11;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Preset Track Data ─────────────────────────────────────────────────────────
def parse_track_csv(source):
    """Parse track CSV from a filepath string or file-like object.
    Expected columns: x_m, y_m, w_tr_right_m, w_tr_left_m"""
    import csv, io
    xs, ys, wr_list, wl_list = [], [], [], []
    if isinstance(source, str):
        f = open(source)
    else:
        # Streamlit UploadedFile — read bytes and decode
        raw = source.read()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        f = io.StringIO(raw)
    reader = csv.reader(f)
    for row in reader:
        if not row or row[0].strip().startswith('#'):
            continue
        try:
            xs.append(float(row[0])); ys.append(float(row[1]))
            wr_list.append(float(row[2])); wl_list.append(float(row[3]))
        except ValueError:
            continue  # skip header rows with non-numeric data
    if isinstance(source, str):
        f.close()
    x, y = np.array(xs), np.array(ys)
    wr, wl = np.array(wr_list), np.array(wl_list)
    dx, dy = np.gradient(x), np.gradient(y)
    norm = np.sqrt(dx**2 + dy**2) + 1e-9
    nx, ny = -dy / norm, dx / norm
    outer = np.column_stack([x + wr * nx, y + wr * ny])
    inner = np.column_stack([x - wl * nx, y - wl * ny])
    center = np.column_stack([x, y])
    return outer, inner, center

def get_track(name, uploaded_csv=None):
    """Returns (outer_wall, inner_wall, center) as arrays of (x, y) points"""
    if name == "📂 Upload CSV..." and uploaded_csv is not None:
        return parse_track_csv(uploaded_csv)
    elif name == "Monza":
        return parse_track_csv("Monza.csv")
    elif name == "Spa-Francorchamps":
        t = np.linspace(0, 2 * np.pi, 150)
        x = 3 * np.cos(t) + 0.6 * np.cos(2 * t) + 0.2 * np.cos(5 * t)
        y = 2.2 * np.sin(t) + 0.4 * np.sin(3 * t)
        width = 0.16
    elif name == "Suzuka":
        t = np.linspace(0, 2 * np.pi, 130)
        x = 2.8 * np.cos(t) + 0.5 * np.sin(2 * t) + 0.2 * np.cos(4 * t)
        y = 2.0 * np.sin(t) + 0.3 * np.cos(3 * t)
        width = 0.15
    elif name == "Silverstone":
        t = np.linspace(0, 2 * np.pi, 140)
        x = 3.2 * np.cos(t) + 0.4 * np.cos(2 * t) + 0.1 * np.sin(5 * t)
        y = 1.6 * np.sin(t) + 0.5 * np.sin(3 * t)
        width = 0.17
    else:
        t = np.linspace(0, 2 * np.pi, 120)
        x = 3 * np.cos(t)
        y = 2 * np.sin(t)
        width = 0.15

    dx = np.gradient(x)
    dy = np.gradient(y)
    norm = np.sqrt(dx**2 + dy**2) + 1e-9
    nx = -dy / norm
    ny = dx / norm
    outer = np.column_stack([x + width * nx, y + width * ny])
    inner = np.column_stack([x - width * nx, y - width * ny])
    center = np.column_stack([x, y])
    return outer, inner, center

# ── Build Q matrix ────────────────────────────────────────────────────────────
def build_Q(n):
    Q = np.zeros((n, n))
    for i in range(1, n - 1):
        Q[i, i - 1] = -1
        Q[i, i] = 2
        Q[i, i + 1] = -1
    Q[0, 0] = 2; Q[0, 1] = -1
    Q[-1, -1] = 2; Q[-1, -2] = -1
    return Q

# ── Compute track curvature at each point ─────────────────────────────────────
def compute_track_curvature(center):
    """Returns signed curvature at each point along the center line.
    Positive = left turn, Negative = right turn (from car's perspective)."""
    n = len(center)
    curvature = np.zeros(n)
    for i in range(n):
        p0 = center[(i - 1) % n]
        p1 = center[i]
        p2 = center[(i + 1) % n]
        v1 = p1 - p0
        v2 = p2 - p1
        # signed cross product: positive = left bend, negative = right bend
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        denom = (np.linalg.norm(v1) * np.linalg.norm(v2)) + 1e-9
        curvature[i] = cross / denom
    return curvature

# ── Compute racing line from alpha ────────────────────────────────────────────
def alpha_to_line(alpha, outer, inner):
    return outer * alpha[:, None] + inner * (1 - alpha[:, None])

# ── Compute speed profile ─────────────────────────────────────────────────────
def compute_speed_profile(line, mu, cl, cd, rho=1.225, A=2.0, m=1400):
    n = len(line)
    speeds = np.zeros(n)
    g = 9.81
    for i in range(n):
        p1 = line[i]
        p2 = line[(i + 1) % n]
        p0 = line[(i - 1) % n]
        v1 = p2 - p1
        v2 = p1 - p0
        cross = abs(v1[0] * v2[1] - v1[1] * v2[0])
        denom = (np.linalg.norm(v1) * np.linalg.norm(v2)) + 1e-9
        curvature = cross / (denom + 1e-9)
        r = 1.0 / (curvature + 1e-6)
        # downforce increases grip
        F_down = 0.5 * rho * cl * A
        N = m * g + F_down
        v_max = np.sqrt(mu * g * r * (1 + F_down / (m * g)))
        speeds[i] = min(v_max, 90)  # cap at 90 m/s (~320 km/h)
    return speeds

# ── Compute lateral G ─────────────────────────────────────────────────────────
def compute_lateral_g(line, speeds):
    n = len(line)
    lat_g = np.zeros(n)
    g = 9.81
    for i in range(n):
        p1 = line[i]
        p2 = line[(i + 1) % n]
        p0 = line[(i - 1) % n]
        v1 = p2 - p1
        v2 = p1 - p0
        cross = abs(v1[0] * v2[1] - v1[1] * v2[0])
        denom = (np.linalg.norm(v1) * np.linalg.norm(v2)) + 1e-9
        curvature = cross / (denom + 1e-9)
        r = 1.0 / (curvature + 1e-6)
        lat_g[i] = (speeds[i] ** 2) / (r * g)
    return lat_g

# ── Plot track ────────────────────────────────────────────────────────────────
def plot_track(outer, inner, center, racing_line=None, iteration=None, ghost_lines=None):
    fig = go.Figure()

    # Track surface fill
    fig.add_trace(go.Scatter(
        x=np.append(outer[:, 0], outer[0, 0]),
        y=np.append(outer[:, 1], outer[0, 1]),
        fill='toself',
        fillcolor='rgba(30,30,40,0.9)',
        line=dict(color='#555', width=1.5),
        name='Track Surface',
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=np.append(inner[:, 0], inner[0, 0]),
        y=np.append(inner[:, 1], inner[0, 1]),
        fill='toself',
        fillcolor='rgba(10,10,15,1)',
        line=dict(color='#555', width=1.5),
        name='Inner',
        showlegend=False,
    ))

    # Outer wall
    fig.add_trace(go.Scatter(
        x=np.append(outer[:, 0], outer[0, 0]),
        y=np.append(outer[:, 1], outer[0, 1]),
        mode='lines',
        line=dict(color='rgba(255,255,255,0.27)', width=2),
        name='Outer Wall',

        showlegend=False,
    ))

    # Inner wall
    fig.add_trace(go.Scatter(
        x=np.append(inner[:, 0], inner[0, 0]),
        y=np.append(inner[:, 1], inner[0, 1]),
        mode='lines',
        line=dict(color='rgba(255,255,255,0.27)', width=2),
        name='Inner Wall',
        showlegend=False,
    ))

    # Center line (dashed)
    fig.add_trace(go.Scatter(
        x=np.append(center[:, 0], center[0, 0]),
        y=np.append(center[:, 1], center[0, 1]),
        mode='lines',
        line=dict(color='rgba(255,255,255,0.13)', width=1, dash='dot'),
        name='Center Line',
        showlegend=False,
    ))

    # Ghost lines — past iterations fading out
    # ghost_lines is a list of (line_array, iter_num), oldest first
    if ghost_lines:
        n_ghosts = len(ghost_lines)
        for idx, (ghost, ghost_iter) in enumerate(ghost_lines):
            # fade: oldest ghost is nearly invisible, newest ghost is more visible
            # opacity ramps from 0.04 (oldest) to 0.30 (most recent ghost)
            t = (idx + 1) / n_ghosts  # 0..1, oldest=low, newest=high
            opacity = 0.04 + t * 0.26
            width = 0.8 + t * 1.2  # thin → slightly thicker as we approach current
            # color shifts slightly: older = more blue-ish, newer = more orange
            r = int(180 + t * 75)
            g_ch = int(60 + t * 68)
            b_ch = int(100 - t * 80)
            color = f'rgba({r},{g_ch},{b_ch},{opacity:.2f})'
            fig.add_trace(go.Scatter(
                x=np.append(ghost[:, 0], ghost[0, 0]),
                y=np.append(ghost[:, 1], ghost[0, 1]),
                mode='lines',
                line=dict(color=color, width=width),
                name=f'Iter {ghost_iter}',
                showlegend=False,
            ))

    # Current racing line (bright red, on top)
    if racing_line is not None:
        fig.add_trace(go.Scatter(
            x=np.append(racing_line[:, 0], racing_line[0, 0]),
            y=np.append(racing_line[:, 1], racing_line[0, 1]),
            mode='lines',
            line=dict(color='#ff4444', width=3),
            name=f'Racing Line (iter {iteration})' if iteration else 'Racing Line',
        ))

    title_text = f"🏎  Track Layout" + (f" — Iteration {iteration}" if iteration else "")
    fig.update_layout(
        title=dict(text=title_text, font=dict(family='Orbitron', size=14, color='#ff8800')),
        paper_bgcolor='#0a0a0f',
        plot_bgcolor='#0a0a0f',
        font=dict(family='Rajdhani', color='#aaa'),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor='x'),
        margin=dict(l=20, r=20, t=50, b=20),
        height=480,
        legend=dict(font=dict(family='Rajdhani', color='#aaa'), bgcolor='#0a0a0f'),
    )
    return fig

# ── Plot speed profile ────────────────────────────────────────────────────────
def plot_speed(speeds):
    n = len(speeds)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(n)),
        y=speeds * 3.6,  # m/s to km/h
        mode='lines',
        fill='tozeroy',
        fillcolor='rgba(255,68,68,0.1)',
        line=dict(color='#ff4444', width=2),
        name='Speed',
    ))
    fig.update_layout(
        title=dict(text='Speed Profile (km/h)', font=dict(family='Orbitron', size=12, color='#ff8800')),
        paper_bgcolor='#0a0a0f',
        plot_bgcolor='#0a0a0f',
        font=dict(family='Rajdhani', color='#aaa'),
        xaxis=dict(showgrid=False, title='Segment', color='#666'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.07)', title='km/h', color='#666'),
        margin=dict(l=40, r=20, t=40, b=40),
        height=220,
    )
    return fig

# ── Plot lateral G ────────────────────────────────────────────────────────────
def plot_lat_g(lat_g, mu):
    n = len(lat_g)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(n)),
        y=lat_g,
        mode='lines',
        fill='tozeroy',
        fillcolor='rgba(255,136,0,0.1)',
        line=dict(color='#ff8800', width=2),
        name='Lateral G',
    ))
    fig.add_hline(y=mu, line_dash='dash', line_color='rgba(255,68,68,0.53)',
                  annotation_text='Grip Limit', annotation_font_color='#ff4444')
    fig.update_layout(
        title=dict(text='Lateral G-Force', font=dict(family='Orbitron', size=12, color='#ff8800')),
        paper_bgcolor='#0a0a0f',
        plot_bgcolor='#0a0a0f',
        font=dict(family='Rajdhani', color='#aaa'),
        xaxis=dict(showgrid=False, title='Segment', color='#666'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.07)', title='G', color='#666'),
        margin=dict(l=40, r=20, t=40, b=40),
        height=220,
    )
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="main-title" style="font-size:1.2rem;">⚙ SETUP</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-header">🏁 Track</div>', unsafe_allow_html=True)
    track_name = st.selectbox("Select Track", ["Monza", "Spa-Francorchamps", "Suzuka", "Silverstone", "📂 Upload CSV..."])

    uploaded_csv = None
    if track_name == "📂 Upload CSV...":
        uploaded_csv = st.file_uploader("Drop track CSV here", type=["csv"], label_visibility="collapsed")
        if uploaded_csv is None:
            st.caption("CSV format: x_m, y_m, w_tr_right_m, w_tr_left_m")

    st.markdown('<div class="sidebar-header">💨 Aerodynamics</div>', unsafe_allow_html=True)
    cl = st.slider("Downforce Coefficient (CL)", 0.5, 4.0, 2.5, 0.1)
    cd = st.slider("Drag Coefficient (CD)", 0.5, 2.0, 1.0, 0.1)

    st.markdown('<div class="sidebar-header">🔵 Tyres</div>', unsafe_allow_html=True)
    mu = st.slider("Friction Coefficient (μ)", 0.8, 2.0, 1.4, 0.05)

    st.markdown('<div class="sidebar-header">⚙ Suspension</div>', unsafe_allow_html=True)
    k = st.slider("Spring Stiffness (k)", 10000, 80000, 40000, 5000)
    c = st.slider("Damping (c)", 1000, 8000, 3000, 500)

    st.markdown('<div class="sidebar-header">🔄 Optimizer</div>', unsafe_allow_html=True)
    n_iter = st.slider("Iterations", 5, 100, 30, 5)
    lr = st.slider("Learning Rate", 0.01, 0.5, 0.1, 0.01)

    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("▶  RUN OPTIMIZER")
    reset_btn = st.button("↺  RESET")

# ── Main Layout ───────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">GT RACING LINE SIMULATOR</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Linear Algebra · Physics Simulation · GT Motorsport</div>', unsafe_allow_html=True)

# Load track — handle upload mode
if track_name == "📂 Upload CSV..." and uploaded_csv is None:
    st.info("⬆ Drop a track CSV in the sidebar to get started — format: `x_m, y_m, w_tr_right_m, w_tr_left_m`")
    st.stop()

# use uploaded filename as unique track ID so reset triggers on new file
track_id = uploaded_csv.name if (track_name == "📂 Upload CSV..." and uploaded_csv) else track_name
outer, inner, center = get_track(track_name, uploaded_csv)
n_seg = len(center)

# Init alpha — reset if track changed or explicit reset
if 'alpha' not in st.session_state or reset_btn or st.session_state.get('track_name') != track_id:
    st.session_state.alpha = np.full(n_seg, 0.5)
    st.session_state.iteration = 0
    st.session_state.running = False
    st.session_state.cost_history = []
    st.session_state.ghost_lines = []
    st.session_state.track_name = track_id
    st.session_state.optimized = False  # flag: has optimizer run at least once?

alpha = st.session_state.alpha
optimized = st.session_state.get('optimized', False)

# only compute metrics if we have an actual racing line to show
if optimized:
    racing_line = alpha_to_line(alpha, outer, inner)
    speeds = compute_speed_profile(racing_line, mu, cl, cd)
    lat_g = compute_lateral_g(racing_line, speeds)
else:
    racing_line = None
    speeds = np.zeros(n_seg)
    lat_g = np.zeros(n_seg)

# ── Top metrics row ───────────────────────────────────────────────────────────

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    val = f"{speeds.max()*3.6:.0f}" if optimized else "—"
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Max Speed</div>
        <div class="metric-value">{val}<span class="metric-unit">{"km/h" if optimized else ""}</span></div>
    </div>""", unsafe_allow_html=True)
with col2:
    val = f"{speeds.min()*3.6:.0f}" if optimized else "—"
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Min Speed</div>
        <div class="metric-value">{val}<span class="metric-unit">{"km/h" if optimized else ""}</span></div>
    </div>""", unsafe_allow_html=True)
with col3:
    val = f"{lat_g.max():.2f}" if optimized else "—"
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Max Lateral G</div>
        <div class="metric-value">{val}<span class="metric-unit">{"G" if optimized else ""}</span></div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Segments</div>
        <div class="metric-value">{n_seg}<span class="metric-unit">pts</span></div>
    </div>""", unsafe_allow_html=True)
with col5:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Iteration</div>
        <div class="metric-value">{st.session_state.iteration}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ── Main plots ────────────────────────────────────────────────────────────────
col_track, col_graphs = st.columns([1.5, 1])

track_placeholder = col_track.empty()
speed_placeholder = col_graphs.empty()
g_placeholder = col_graphs.empty()
iter_placeholder = st.empty()

def render(alpha, iteration, ghost_lines=None, show_line=True):
    rl = alpha_to_line(alpha, outer, inner) if show_line else None
    spd = compute_speed_profile(rl, mu, cl, cd) if show_line else np.zeros(n_seg)
    lg = compute_lateral_g(rl, spd) if show_line else np.zeros(n_seg)
    track_placeholder.plotly_chart(
        plot_track(outer, inner, center, rl, iteration, ghost_lines=ghost_lines),
        use_container_width=True
    )
    speed_placeholder.plotly_chart(plot_speed(spd), use_container_width=True)
    g_placeholder.plotly_chart(plot_lat_g(lg, mu), use_container_width=True)
    return rl, spd, lg

# Initial render — only show racing line if already optimized
render(alpha, st.session_state.iteration,
       ghost_lines=st.session_state.get('ghost_lines', []),
       show_line=optimized)

# ── Optimizer loop ────────────────────────────────────────────────────────────
if run_btn:
    st.session_state.optimized = True
    Q = build_Q(n_seg)
    alpha = st.session_state.alpha.copy()
    MAX_GHOSTS = 8
    GHOST_EVERY = max(1, n_iter // 12)

    # Compute signed curvature of the track center line
    curv = compute_track_curvature(center)

    # Normalize curvature to [-1, 1]
    curv_max = np.abs(curv).max() + 1e-9
    curv_norm = curv / curv_max  # positive = left bend, negative = right bend

    # apex_target: where the line SHOULD be in corners
    # In a left bend (curv > 0): go to inner wall (alpha → 0, i.e. inner)
    # In a right bend (curv < 0): go to inner wall from right (alpha → 1, i.e. outer... wait)
    # alpha=0 → inner wall, alpha=1 → outer wall
    # For left corners: cut inside = alpha=0; for right corners: cut inside = alpha=1
    # So: apex_target = 0.5 - 0.5 * sign(curv) * |curv_norm|
    # On straights (curv≈0): target stays at 0.5
    corner_strength = 2.5  # how aggressively to target apex vs smoothness
    apex_target = 0.5 - 0.5 * curv_norm  # left bend → 0, right bend → 1, straight → 0.5

    for i in range(n_iter):
        # save ghost BEFORE updating alpha
        if i % GHOST_EVERY == 0:
            ghost_line = alpha_to_line(alpha, outer, inner)
            st.session_state.ghost_lines.append((ghost_line.copy(), st.session_state.iteration))
            if len(st.session_state.ghost_lines) > MAX_GHOSTS:
                st.session_state.ghost_lines = st.session_state.ghost_lines[-MAX_GHOSTS:]

        # Smoothness gradient from Q matrix
        grad_smooth = 2 * Q @ alpha

        # Apex-targeting gradient: pull alpha toward apex_target at corners
        # Weight by |curvature| so straights are barely affected
        apex_weight = np.abs(curv_norm)  # 0 on straights, 1 at sharpest corner
        grad_apex = corner_strength * apex_weight * (alpha - apex_target)

        grad = grad_smooth + grad_apex
        alpha = alpha - lr * grad
        alpha = np.clip(alpha, 0.05, 0.95)
        st.session_state.iteration += 1
        cost = float(alpha @ Q @ alpha)
        st.session_state.cost_history.append(cost)

        render(alpha, st.session_state.iteration, ghost_lines=st.session_state.ghost_lines)
        iter_placeholder.markdown(
            f'<div class="iter-text">OPTIMIZING · ITERATION {st.session_state.iteration} · COST {cost:.4f}</div>',
            unsafe_allow_html=True
        )
        time.sleep(0.05)

    st.session_state.alpha = alpha
    iter_placeholder.markdown(
        f'<div class="iter-text" style="color:#44ff44;">✓ OPTIMIZATION COMPLETE · FINAL COST {cost:.4f}</div>',
        unsafe_allow_html=True
    )

# ── Cost history ──────────────────────────────────────────────────────────────
if st.session_state.cost_history:
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown('<p style="font-family:Orbitron;font-size:0.8rem;color:#ff8800;letter-spacing:2px;">CONVERGENCE HISTORY</p>', unsafe_allow_html=True)
    fig_cost = go.Figure()
    fig_cost.add_trace(go.Scatter(
        y=st.session_state.cost_history,
        mode='lines+markers',
        line=dict(color='#ffcc00', width=2),
        marker=dict(color='#ff4444', size=4),
        name='Cost αᵀQα',
    ))
    fig_cost.update_layout(
        paper_bgcolor='#0a0a0f',
        plot_bgcolor='#0a0a0f',
        font=dict(family='Rajdhani', color='#aaa'),
        xaxis=dict(showgrid=False, title='Iteration', color='#666'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.07)', title='Cost', color='#666'),
        margin=dict(l=40, r=20, t=20, b=40),
        height=200,
    )
    st.plotly_chart(fig_cost, use_container_width=True)