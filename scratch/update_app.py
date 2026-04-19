import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add imports
content = content.replace('import time\n', 'import time\nfrom scipy.linalg import lu_factor, lu_solve\nfrom suspension import render_suspension_tab\nfrom telemetry import render_telemetry_tab\n')

# 2. Add Exact Solve button
content = content.replace('    run_btn = st.button(" RUN OPTIMIZER")\n    reset_btn = st.button(" RESET")', 
                          '    run_btn = st.button(" RUN ITERATIVE")\n    run_exact_btn = st.button("EXACT SOLVE (LU)")\n    reset_btn = st.button(" RESET")')

# 3. Add tabs after subtitle
main_layout_start = content.find('# Load track — handle upload mode')
subtitle_idx = content.rfind('</div>\', unsafe_allow_html=True)', 0, main_layout_start) + len('</div>\', unsafe_allow_html=True)') + 1

tabs_code = """
tab_line, tab_susp, tab_pca = st.tabs(["Racing Line Solver", "Suspension Dynamics (Eigenvalues)", "Telemetry PCA (SVD)"])

with tab_line:
"""

content = content[:subtitle_idx] + '\n' + tabs_code + content[subtitle_idx:]

# Now everything from subtitle_idx down is in tab_line. We need to indent it all.
# Actually, Streamlit tabs can be done using `with` or just using the objects.
# Let's indent everything from `# Load track` downwards.
lines = content[subtitle_idx + len(tabs_code):].split('\n')
indented_lines = ['    ' + line for line in lines]
content = content[:subtitle_idx + len(tabs_code)] + '\n'.join(indented_lines)

# 4. Insert exact solver logic
exact_solve_code = """
    # ── Exact Solver (LU) ─────────────────────────────────────────────────────────
    if run_exact_btn:
        st.session_state.optimized = True
        Q_mat = build_Q(n_seg)
        curv = compute_track_curvature(center)
        curv_max = np.abs(curv).max() + 1e-9
        curv_norm = curv / curv_max
        
        corner_strength = 2.5
        apex_target = 0.5 - 0.5 * curv_norm
        apex_weight = np.abs(curv_norm)
        
        # System: (2Q + diag(W)) alpha = W * apex_target
        W = corner_strength * apex_weight
        A_mat = 2 * Q_mat + np.diag(W)
        B_mat = W * apex_target
        
        start_time = time.time()
        lu, piv = lu_factor(A_mat)
        alpha_exact = lu_solve((lu, piv), B_mat)
        solve_time = time.time() - start_time
        
        alpha_exact = np.clip(alpha_exact, 0.05, 0.95)
        st.session_state.alpha = alpha_exact
        st.session_state.iteration = 1
        st.session_state.cost_history = [float(alpha_exact @ Q_mat @ alpha_exact)]
        st.session_state.ghost_lines = []
        
        iter_placeholder.markdown(
            f'<div class="iter-text" style="color:#44ff44;">EXACT SOLVE (LU) COMPLETE ({solve_time*1000:.1f} ms) · COST {st.session_state.cost_history[0]:.4f}</div>',
            unsafe_allow_html=True
        )
        alpha = alpha_exact
        optimized = True
        render(alpha, 1, show_line=True)
"""
# insert before iterative optimizer
run_btn_idx = content.find('    if run_btn:')
content = content[:run_btn_idx] + exact_solve_code + '\n' + content[run_btn_idx:]

# 5. Add rendering for tabs 2 and 3 at the very end
tabs_end_code = """

with tab_susp:
    render_suspension_tab(k, c, 1400)

with tab_pca:
    # Need speeds and lat_g and alpha and curv. We have them from tab_line.
    # Pass them to telemetry
    curv = compute_track_curvature(center)
    render_telemetry_tab(speeds, lat_g, alpha, curv)
"""
content += tabs_end_code

with open('app_new.py', 'w', encoding='utf-8') as f:
    f.write(content)
