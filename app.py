import streamlit as st
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
    st.image("https://cdn-icons-png.flaticon.com/512/5758/5758248.png", width=50)
    st.markdown("### CFD Studio")
    
    # 更加现代的导航
    mode = st.radio(
        "MENU", 
        ["Home", "Simulation", "Knowledge Base"], 
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.info("**Tip:** 推荐使用深色模式或高对比度显示器以获得最佳图表体验。")
    st.markdown('<div class="sidebar-copyright">© 2025 chunfengfusu | Ver 4.2</div>', unsafe_allow_html=True)

# ==============================================================================
# 模块 1: Home (项目介绍)
# ==============================================================================
if mode == "Home":
    st.session_state.reading_article = None
    
    layout.render_hero_header()
    
    col_intro, col_img = st.columns([1, 1])
    
    with col_intro:
        st.markdown("""
        ### 👋 欢迎使用
        这是一个基于有限差分法 (Finite Difference Method) 的二维方腔流数值模拟平台。
        
        **核心功能：**
        * 🌊 **实时求解**：基于 N-S 方程的 Python 原生求解器。
        * 📊 **交互可视化**：流线、压力场、速度场实时渲染。
        * 📚 **理论支持**：内置完整的计算流体力学 (CFD) 教程。
        
        点击左侧 **Simulation** 开始您的第一次计算。
        """)
        
    with col_img:
        img_path = os.path.join("assets", "cover.jpg")
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
            st.caption("Standard Lid-Driven Cavity Flow Result")

# ==============================================================================
# 模块 2: Simulation (计算模拟)
# ==============================================================================
elif mode == "Simulation":
    st.session_state.reading_article = None
    
    st.markdown("## 🌪️ Simulation Workspace")
    
    # 两列布局：左侧参数面板，右侧结果/说明
    main_col1, main_col2 = st.columns([1, 2.5])
    
    with main_col1:
        with st.form("cfd_params_form"):
            st.markdown("### ⚙️ Parameters")
            
            st.markdown("**Physics**")
            re_num = st.number_input("Reynolds Number (Re)", 1.0, 5000.0, 100.0, 10.0)
            
            st.markdown("**Discretization**")
            grid_size = st.slider("Grid Resolution (Nx=Ny)", 21, 151, 41, 10)
            time_step = st.number_input("Time Step (dt)", 0.0001, 0.1, 0.001, format="%.4f")
            
            with st.expander("Advanced Solver Settings"):
                max_iter = st.number_input("Max Iterations", 500, 20000, 2000, step=500)
                omega = st.slider("SOR Relaxation (ω)", 1.0, 1.95, 1.8)
            
            st.write("")
            submitted = st.form_submit_button("🚀 Run Simulation", use_container_width=True)

    with main_col2:
        # B. 计算逻辑
        if submitted:
            with st.status("Solving Navier-Stokes Equations...", expanded=True) as status:
                st.write("Initializing Grid...")
                try:
                    u, v, p = solve_cavity(re_num, grid_size, grid_size, max_iter, time_step, 1e-5, omega)
                    st.session_state.cfd_result = {"u": u, "v": v, "p": p, "re": re_num, "grid": grid_size}
                    status.update(label="Calculation Complete!", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="Error Occurred", state="error")
                    st.error(f"Solver Error: {e}")

        # C. 结果展示
        if st.session_state.cfd_result:
            res = st.session_state.cfd_result
            
            # 顶部指标栏
            m1, m2, m3 = st.columns(3)
            m1.metric("Reynolds Number", int(res['re']))
            m2.metric("Grid Points", f"{res['grid']} x {res['grid']}")
            m3.metric("Max Velocity", f"{np.max(np.sqrt(res['u']**2 + res['v']**2)):.2f}")
            
            st.markdown("---")
            
            # 图表展示区
            st.markdown("### 📊 Visualization Results")
            
            # 第一行图表
            row1_1, row1_2 = st.columns(2)
            with row1_1:
                fig1 = plots.plot_velocity_magnitude(res['u'], res['v'], res['grid'], res['re'])
                layout.render_plot_with_caption(fig1, "Velocity Magnitude")
            with row1_2:
                fig2 = plots.plot_streamlines(res['u'], res['v'], res['grid'], res['re'])
                layout.render_plot_with_caption(fig2, "Streamlines & Topology")
                
            # 第二行图表 (居中或全宽)
            st.write("")
            row2_1, row2_2, row2_3 = st.columns([1, 2, 1])
            with row2_2:
                fig3 = plots.plot_pressure(res['p'], res['grid'], res['re'])
                layout.render_plot_with_caption(fig3, "Pressure Distribution")

        else:
            # 初始占位符
            st.info("👈 Please set parameters on the left and click 'Run Simulation'.")
            st.image("https://upload.wikimedia.org/wikipedia/commons/e/e2/Lid_driven_cavity_flow_Re_1000.gif", caption="Example: Unsteady Cavity Flow (Ref)", width=400)

# ==============================================================================
# 模块 3: Knowledge Base (知识库)
# ==============================================================================
elif mode == "Knowledge Base":
    
    if st.session_state.reading_article:
        article = st.session_state.reading_article
        
        # 顶部导航条
        st.button("⬅️ Back to Library", on_click=lambda: st.session_state.update(reading_article=None))
        
        st.markdown(f"## {article['title']}")
        st.markdown("---")
        reader.render_content("posts", article['file'])

    else:
        st.markdown("## 📚 Knowledge Base")
        st.markdown("Explore the theory behind the simulation.")
        st.write("")
        
        articles = reader.load_catalog("posts")
        if articles:
            # 自动网格布局
            cols = st.columns(2) # 两列显示文章卡片，更美观
            for i, article in enumerate(articles):
                with cols[i % 2]:
                    if layout.render_card_standard(article, i):
                        st.session_state.reading_article = article
                        st.rerun()
        else:
            st.warning("No articles found in posts/catalog.json")