import streamlit as st
import numpy as np
import plotly.graph_objects as go

def render_telemetry_tab(speeds, lat_g, alpha, curv):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Telemetry Analysis (PCA via SVD)")
    st.markdown('''
    Modern race teams analyze thousands of telemetry points per lap. Here, we use **Singular Value Decomposition (SVD)** to perform **Principal Component Analysis (PCA)** on our lap data.
    By finding the eigenvectors of the Covariance matrix, we reduce the data to the most important "Principal Components" that define the car's performance signature.
    ''')
    
    if len(speeds) == 0 or np.all(speeds == 0):
        st.info("Run the optimizer first to generate telemetry data!")
        return

    # Build data matrix X (n_samples, n_features)
    # Features: Speed, Lat_G, Alpha (position), Curvature
    # Ensure all are column vectors
    speeds = np.array(speeds).reshape(-1, 1)
    lat_g = np.array(lat_g).reshape(-1, 1)
    alpha = np.array(alpha).reshape(-1, 1)
    curv = np.array(curv).reshape(-1, 1)
    
    X = np.hstack([speeds, lat_g, alpha, curv])
    feature_names = ["Speed", "Lat G", "Track Pos (α)", "Curvature"]
    
    # 1. Standardize the data (mean=0, variance=1)
    X_mean = np.mean(X, axis=0)
    X_std = np.std(X, axis=0) + 1e-9
    X_norm = (X - X_mean) / X_std
    
    # 2. Covariance Matrix
    n = X_norm.shape[0]
    Cov = (X_norm.T @ X_norm) / (n - 1)
    
    # 3. SVD
    U, S, Vt = np.linalg.svd(Cov)
    # S contains eigenvalues of Cov, Vt contains eigenvectors (Principal Components)
    
    # Project data onto top 2 components
    PC1 = X_norm @ Vt[0, :].T
    PC2 = X_norm @ Vt[1, :].T
    
    # Explained variance
    explained_variance = (S / np.sum(S)) * 100

    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown("#### The Covariance Matrix")
        # Format matrix for latex
        cov_str = " \\\\ ".join([" & ".join([f"{val:.2f}" for val in row]) for row in Cov])
        st.latex(f"C = \\begin{{bmatrix}} {cov_str} \\end{{bmatrix}}")
        st.caption("Features: " + ", ".join(feature_names))
        
        st.markdown("#### Singular Values (Σ)")
        st.latex(f"\\Sigma = \\text{{diag}}({', '.join([f'{s:.2f}' for s in S])})")
        
        st.markdown("#### Variance Explained")
        for i, var in enumerate(explained_variance):
            st.write(f"**PC{i+1}:** {var:.1f}%")
            
    with col2:
        st.markdown(f"#### PCA Projection (Top 2 Components)")
        # Plot PC1 vs PC2, colored by Speed
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=PC1,
            y=PC2,
            mode='markers',
            marker=dict(
                size=6,
                color=speeds.flatten(), # color by speed
                colorscale='Inferno',
                showscale=True,
                colorbar=dict(title="Speed (m/s)")
            ),
            text=[f"Speed: {s[0]:.1f}<br>G: {g[0]:.2f}" for s, g in zip(speeds, lat_g)],
            hoverinfo='text'
        ))
        fig.update_layout(
            xaxis_title=f"Principal Component 1 ({explained_variance[0]:.1f}%)",
            yaxis_title=f"Principal Component 2 ({explained_variance[1]:.1f}%)",
            paper_bgcolor='#0a0a0f',
            plot_bgcolor='#0a0a0f',
            font=dict(family='Rajdhani', color='#aaa'),
            margin=dict(l=40, r=20, t=40, b=40),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # PCA Loadings
        st.markdown("**PC1 Loadings (What does PC1 represent?):**")
        loadings = Vt[0, :]
        loadings_str = " | ".join([f"{name}: {val:+.2f}" for name, val in zip(feature_names, loadings)])
        st.code(loadings_str)
