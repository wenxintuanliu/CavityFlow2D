import streamlit as st
import os

# 1. 页面配置
st.set_page_config(page_title="CFD Studio", layout="wide")

from core.solver import solve_cavity
from viz import plots
from ui import layout, reader

# 2. 注入样式
layout.apply_custom_style()

# 3. 状态管理
if 'reading_article' not in st.session_state:
    st.session_state.reading_article = None
if 'cfd_result' not in st.session_state:
    st.session_state.cfd_result = None

# ==============================================================================
# 左侧栏 (Sidebar) - 固定头部防止跳动
# ==============================================================================
with st.sidebar:
    # 头部固定区域
    with st.container():
        st.image("https://cdn-icons-png.flaticon.com/512/5758/5758248.png", width=60)
        st.title("CFD Studio")
        st.caption("Ver 4.1 | Stable Release")
    
    st.markdown("---")
    
    # 导航菜单
    mode = st.radio(
        "导航菜单", 
        ["项目介绍", "CFD计算模拟", "知识库/文章"], 
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # 版权页脚 (无背景，高级黑)
    st.markdown('<div class="sidebar-copyright">© 2025 chunfengfusu. Some rights reserved.</div>', unsafe_allow_html=True)

# ==============================================================================
# 模块 1: 项目介绍
# ==============================================================================
if mode == "项目介绍":
    st.session_state.reading_article = None
    
    st.header("📖 项目介绍")
    st.divider()
    
    # A. 渲染文字
    # 现在使用的是 iframe 渲染，如果你的 html 里有滚动条，这里就会显示滚动条
    if os.path.exists("posts/about.html"):
        reader.render_content("posts", "about.html")
    else:
        st.info("ℹ️ posts/about.html 未找到")

    st.markdown("---")

    # B. 渲染图片
    img_path = os.path.join("assets", "cover.jpg")
    if os.path.exists(img_path):
        st.markdown("#### 📸 可视化展示")
        # 1:2:1 布局
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.image(img_path, caption="Lid-Driven Cavity Flow Result", use_container_width=True)

# ==============================================================================
# 模块 2: CFD 计算模拟
# ==============================================================================
elif mode == "CFD计算模拟":
    st.session_state.reading_article = None
    st.header("🌪️ 方腔流数值模拟")
    
    # A. 参数表单 (CSS 已去除按钮背景色)
    with st.form("cfd_params_form"):
        st.subheader("1. 模拟参数配置")
        
        c1, c2, c3 = st.columns(3)
        with c1: re_num = st.number_input("雷诺数 (Re)", 1.0, 5000.0, 100.0, 10.0)
        with c2: grid_size = st.slider("网格密度 (Nx=Ny)", 21, 201, 41, 10)
        with c3: time_step = st.number_input("时间步长 (dt)", 0.0001, 0.1, 0.001, format="%.4f")
            
        c4, c5, c6 = st.columns(3)
        with c4: max_iter = st.number_input("最大迭代步数", 500, 20000, 2000, step=500)
        with c5: omega = st.slider("SOR 松弛因子", 1.0, 1.95, 1.8)
        with c6: st.write("") 
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 开始计算 (Start Calculation)", use_container_width=True)

    st.divider()

    # B. 计算逻辑
    if submitted:
        with st.spinner("正在进行 N-S 方程求解..."):
            try:
                u, v, p = solve_cavity(re_num, grid_size, grid_size, max_iter, time_step, 1e-5, omega)
                st.session_state.cfd_result = {"u": u, "v": v, "p": p, "re": re_num, "grid": grid_size}
                st.success("✅ 计算完成")
            except Exception as e:
                st.error(f"Error: {e}")

    # C. 结果展示
    if st.session_state.cfd_result:
        res = st.session_state.cfd_result
        st.subheader(f"2. 模拟结果可视化 (Re={res['re']})")
        
        plot_cols = st.columns(3)
        with plot_cols[0]:
            fig1 = plots.plot_velocity_magnitude(res['u'], res['v'], res['grid'], res['re'])
            layout.render_plot_with_caption(fig1, "Velocity Magnitude", "#e7f5ff")
        with plot_cols[1]:
            fig2 = plots.plot_streamlines(res['u'], res['v'], res['grid'], res['re'])
            layout.render_plot_with_caption(fig2, "Streamlines", "#fff3bf")
        with plot_cols[2]:
            fig3 = plots.plot_pressure(res['p'], res['grid'], res['re'])
            layout.render_plot_with_caption(fig3, "Pressure Field", "#ffe3e3")
    else:
        st.info("👆 请设置参数并点击“开始计算”按钮。")

# ==============================================================================
# 模块 3: 知识库/文章
# ==============================================================================
elif mode == "知识库/文章":
    
    if st.session_state.reading_article:
        article = st.session_state.reading_article
        
        col_btn, col_txt = st.columns([1, 6])
        with col_btn:
            if st.button("⬅️ 返回", use_container_width=True):
                st.session_state.reading_article = None
                st.rerun()
        with col_txt:
            st.markdown(f"### {article['title']}")
            
        st.divider()
        
        # 文章内容渲染 (这里如果是 html 文件，也会用 iframe，解决源码外泄问题)
        reader.render_content("posts", article['file'])

    else:
        st.header("📚 知识库")
        st.divider()
        
        articles = reader.load_catalog("posts")
        if articles:
            cols = st.columns(3)
            for i, article in enumerate(articles):
                with cols[i % 3]:
                    if layout.render_card_standard(article, i):
                        st.session_state.reading_article = article
                        st.rerun()
        else:
            st.warning("暂无文章配置 (posts/catalog.json)")
