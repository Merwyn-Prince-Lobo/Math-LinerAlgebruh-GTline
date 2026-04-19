import streamlit as st
import numpy as np
import plotly.graph_objects as go

def render_suspension_tab(k, c, m=1400):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Suspension State-Space Model (Eigenvalues)")
    st.markdown(r'''
    We model a quarter-car suspension using the differential equation:
    $$ m\ddot{x} + c\dot{x} + kx = F_{road} $$
    Converting to a state-space linear system $\dot{X} = AX$, where $X = \begin{bmatrix} x \\ \dot{x} \end{bmatrix}$:
    $$ A = \begin{bmatrix} 0 & 1 \\ -k/m & -c/m \end{bmatrix} $$
    ''')
    
    A_sys = np.array([
        [0, 1],
        [-k/m, -c/m]
    ])
    
    # Compute Eigenvalues
    eigenvalues, eigenvectors = np.linalg.eig(A_sys)
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown("#### System Matrix A")
        st.latex(f"A = \\begin{{bmatrix}} 0 & 1 \\\\ {A_sys[1,0]:.2f} & {A_sys[1,1]:.2f} \\end{{bmatrix}}")
        
        st.markdown("#### Eigenvalues (λ)")
        for i, val in enumerate(eigenvalues):
            if np.iscomplex(val):
                st.latex(f"\\lambda_{i+1} = {val.real:.2f} {val.imag:+.2f}i")
            else:
                st.latex(f"\\lambda_{i+1} = {val.real:.2f}")
                
        # Analysis based on positive definiteness / eigenvalues
        st.markdown("#### Dynamic Analysis")
        is_complex = np.iscomplexobj(eigenvalues) or np.any(np.iscomplex(eigenvalues))
        if is_complex:
            st.warning("**Underdamped System (Oscillatory):** The eigenvalues have imaginary components. The car will bounce over curbs.")
        else:
            if eigenvalues[0].real == eigenvalues[1].real:
                st.success("**Critically Damped:** The eigenvalues are real and equal. Optimal return to equilibrium.")
            else:
                st.info("**Overdamped:** The eigenvalues are real and distinct. Sluggish response to curbs.")
                
        if np.all(np.real(eigenvalues) < 0):
            st.success("**Stable:** All real parts of eigenvalues are negative.")
        else:
            st.error("**Unstable!** System will diverge.")

    with col2:
        st.markdown("#### Curb Hit Response Simulation")
        # Simulate step response (hitting a 5cm curb)
        dt = 0.01
        t = np.arange(0, 3.0, dt)
        X = np.array([0.05, 0.0]) # Initial displacement 5cm, 0 velocity
        history = []
        for _ in t:
            history.append(X[0])
            # Euler integration: X_new = X + dX*dt = X + (A@X)*dt
            # Or better, exact using eigenvalues, but euler is fine for visualization
            X = X + (A_sys @ X) * dt
            
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t, y=np.array(history)*100, mode='lines', line=dict(color='#ff8800', width=3)))
        fig.add_hline(y=0, line_dash="dash", line_color="#fff", opacity=0.3)
        fig.update_layout(
            title="Suspension Vertical Displacement",
            xaxis_title="Time (s)",
            yaxis_title="Displacement (cm)",
            paper_bgcolor='#0a0a0f',
            plot_bgcolor='#0a0a0f',
            font=dict(family='Rajdhani', color='#aaa'),
            margin=dict(l=40, r=20, t=40, b=40),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
