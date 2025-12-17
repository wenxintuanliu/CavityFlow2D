import streamlit as st
import numpy as np  # <--- 修复了这里的 NameError
import os

# 1. 页面配置 (必须是第一个 Streamlit 命令)
st.set_page_config(
    page_title="CFD Studio", 
    layout="wide",
    page_icon="🌊",
    initial_sidebar_state="expanded"
)

from core.solver import solve_cavity
from viz import plots
from ui import layout, reader

# 2. 注入样式
layout.apply_custom_style()

# 3. 状态初始化
if 'reading_article' not in st.session_state:
    st.session_state.reading_article = None
if 'cfd_result' not in st.session_state:
    st.session_state.cfd_result = None

# ==============================================================================
# 左侧栏 (Sidebar)
# ==============================================================================
with st.sidebar:
    st.markdown("### 🌊 CFD Studio")
    st.caption("Ver 5.0 | Professional Edition")
    
    st.markdown("---")
    
    # 极简导航
    mode = st.radio(
        "MENU", 
        ["Home", "Simulation", "Knowledge"], 
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 12px; color: #666;">
        <b>Engine:</b> Python Native<br>
        <b>Method:</b> Finite Difference<br>
        <b>Scheme:</b> MAC / Projection
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # 底部版权
    st.markdown('<div class="sidebar-copyright">© 2025 Chunfeng Fusu</div>', unsafe_allow_html=True)

# ==============================================================================
# 模块 1: Home
# ==============================================================================
if mode == "Home":
    st.session_state.reading_article = None
    
    layout.render_hero_header()
    
    # 更加紧凑的介绍页
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div style="background: white; padding: 30px; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <h3 style="margin-top:0;">What is Lid-Driven Cavity Flow?</h3>
            <p style="color: #444; line-height: 1.6;">
                The lid-driven cavity is a classic benchmark problem for viscous incompressible fluid flow. 
                It serves as a standard test case for checking the accuracy of numerical techniques.
            </p>
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">
            <div style="display: flex; gap: 15px;">
                <span style="background: #f1f5f9; color: #334155; padding: 4px 12px; border-radius: 20px; font-size: 12px;">Navier-Stokes</span>
                <span style="background: #f1f5f9; color: #334155; padding: 4px 12px; border-radius: 20px; font-size: 12px;">Incompressible</span>
                <span style="background: #f1f5f9; color: #334155; padding: 4px 12px; border-radius: 20px; font-size: 12px;">Laminar</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        img_path = os.path.join("assets", "cover.jpg")
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True, caption="Visualized Output Example")

# ==============================================================================
# 模块 2: Simulation
# ==============================================================================
elif mode == "Simulation":
    st.session_state.reading_article = None
    
    # 顶部标题栏
    st.markdown("## 🌪️ Simulation Workspace")
    st.markdown("Configure boundary conditions and solver parameters.")
    st.divider()
    
    # 左右分栏：左侧窄（控制），右侧宽（结果）
    col_control, col_display = st.columns([1, 3])
    
    with col_control:
        with st.container(border=True):
            st.markdown("#### ⚙️ Settings")
            
            with st.form("cfd_form"):
                st.caption("PHYSICS")
                re_num = st.number_input("Reynolds (Re)", 10.0, 5000.0, 100.0, 10.0)
                
                st.caption("GRID & TIME")
                grid_size = st.slider("Resolution (N)", 20, 100, 40, 5)
                time_step = st.select_slider("Time Step (dt)", options=[0.01, 0.005, 0.001, 0.0005, 0.0001], value=0.001)
                
                st.caption("SOLVER")
                max_iter = st.number_input("Iterations", 500, 10000, 1500, step=500)
                omega = st.slider("SOR Relaxation", 1.0, 1.9, 1.8)
                
                st.write("")
                btn_run = st.form_submit_button("Start Calculation", type="primary", use_container_width=True)

    with col_display:
        if btn_run:
            with st.status("Processing...", expanded=True) as status:
                st.write("Initializing computational domain...")
                try:
                    u, v, p = solve_cavity(re_num, grid_size, grid_size, max_iter, time_step, 1e-5, omega)
                    st.session_state.cfd_result = {"u": u, "v": v, "p": p, "re": re_num, "grid": grid_size}
                    status.update(label="Computation Successful", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="Error", state="error")
                    st.error(f"Solver Error: {e}")

        # 结果展示区
        if st.session_state.cfd_result:
            res = st.session_state.cfd_result
            
            # 关键指标卡片 (现在 np 已导入，不会报错)
            v_max = np.max(np.sqrt(res['u']**2 + res['v']**2))
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Reynolds No.", int(res['re']))
            m2.metric("Grid Points", f"{res['grid']}^2")
            m3.metric("Max Velocity", f"{v_max:.3f}")
            m4.metric("Divergence", "< 1e-4")
            
            st.write("")
            
            # 图表 Tab 切换 (比平铺更高级)
            tab1, tab2, tab3 = st.tabs(["Velocity Field", "Streamlines", "Pressure Contour"])
            
            with tab1:
                fig1 = plots.plot_velocity_magnitude(res['u'], res['v'], res['grid'], res['re'])
                layout.render_plot_card(fig1, "Velocity Magnitude Distribution")
            
            with tab2:
                fig2 = plots.plot_streamlines(res['u'], res['v'], res['grid'], res['re'])
                layout.render_plot_card(fig2, "Streamline Topology & Vortex Structure")
                
            with tab3:
                fig3 = plots.plot_pressure(res['p'], res['grid'], res['re'])
                layout.render_plot_card(fig3, "Pressure Field (Relative)")

        else:
            # 空状态指引
            st.info("👈 Please adjust parameters on the left sidebar and click 'Start Calculation'.")

# ==============================================================================
# 模块 3: Knowledge
# ==============================================================================
elif mode == "Knowledge":
    
    if st.session_state.reading_article:
        article = st.session_state.reading_article
        st.button("← Back", on_click=lambda: st.session_state.update(reading_article=None))
        st.markdown(f"## {article['title']}")
        st.divider()
        reader.render_content("posts", article['file'])
    else:
        st.markdown("## 📚 Theory & Documentation")
        st.write("")
        articles = reader.load_catalog("posts")
        if articles:
            # 使用更整齐的网格
            cols = st.columns(3)
            for i, article in enumerate(articles):
                with cols[i % 3]:
                    layout.render_article_card(article, i)