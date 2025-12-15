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
# 左侧栏 (侧边栏)
# ==============================================================================
with st.sidebar:
    st.title("🌊 CFD Studio")
    st.caption("Ver 2.0 | Advanced UI")
    st.markdown("---")
    
    # 模式选择 (样式已在 layout.py 中通过 CSS 增加间距)
    mode = st.radio(
        "导航菜单", 
        ["项目介绍", "CFD计算模拟", "知识库/文章"], 
        label_visibility="collapsed"
    )
    
    st.markdown("---")

# ==============================================================================
# 模块 1: 项目介绍
# ==============================================================================
if mode == "项目介绍":
    st.session_state.reading_article = None
    
    st.header("📖 项目介绍")
    st.divider()
    
    # 使用 markdown 渲染，去除滚动条
    if os.path.exists("posts/about.html"):
        reader.render_content("posts", "about.html")
    else:
        st.info("⚠️ 请创建 posts/about.html")

    # 图片展示
    if os.path.exists("assets"):
        images = [f for f in os.listdir("assets") if f.endswith(('.png', '.jpg'))]
        if images:
            st.markdown("#### 📸 可视化展示")
            cols = st.columns(3)
            for idx, img_name in enumerate(images):
                with cols[idx % 3]:
                    st.image(os.path.join("assets", img_name), caption=img_name, use_container_width=True)

# ==============================================================================
# 模块 2: CFD 计算模拟
# ==============================================================================
elif mode == "CFD计算模拟":
    st.session_state.reading_article = None
    st.header("🌪️ 方腔流数值模拟")
    
    # --- 参数设置 ---
    with st.container():
        st.subheader("1. 模拟参数配置")
        
        c1, c2, c3 = st.columns(3)
        with c1: re_num = st.number_input("雷诺数 (Re)", 1.0, 5000.0, 100.0, 10.0)
        with c2: grid_size = st.slider("网格密度 (Nx=Ny)", 21, 201, 41, 10)
        with c3: time_step = st.number_input("时间步长 (dt)", 0.0001, 0.1, 0.001, format="%.4f")
            
        c4, c5, c6 = st.columns(3)
        with c4: max_iter = st.number_input("最大迭代步数", 500, 20000, 2000, step=500)
        with c5: omega = st.slider("SOR 松弛因子", 1.0, 1.95, 1.8)
        
        st.markdown("<br>", unsafe_allow_html=True)
        # 注意：这里 type="primary" 会被 CSS 渲染成鲜艳的渐变色
        start_btn = st.button("🚀 开始计算 (Start Calculation)", type="primary", use_container_width=True)

    st.divider()

    # --- 计算逻辑 ---
    if start_btn:
        with st.spinner("正在进行 N-S 方程求解..."):
            try:
                u, v, p = solve_cavity(re_num, grid_size, grid_size, max_iter, time_step, 1e-5, omega)
                st.session_state.cfd_result = {"u": u, "v": v, "p": p, "re": re_num, "grid": grid_size}
                st.success("✅ 计算完成")
            except Exception as e:
                st.error(f"Error: {e}")

    # --- 结果展示 (三图并列) ---
    if st.session_state.cfd_result:
        res = st.session_state.cfd_result
        st.subheader(f"2. 模拟结果可视化 (Re={res['re']})")
        
        # 修改：使用 3 列布局，而不是 Tabs
        plot_cols = st.columns(3)
        
        # 图 1: 速度云图
        with plot_cols[0]:
            fig1 = plots.plot_velocity_magnitude(res['u'], res['v'], res['grid'], res['re'])
            layout.render_plot_with_caption(fig1, "图1: 速度幅值云图 (Velocity)", "#e7f5ff")
            
        # 图 2: 流线图
        with plot_cols[1]:
            fig2 = plots.plot_streamlines(res['u'], res['v'], res['grid'], res['re'])
            layout.render_plot_with_caption(fig2, "图2: 流线分布 (Streamlines)", "#fff3bf")
            
        # 图 3: 压力场
        with plot_cols[2]:
            fig3 = plots.plot_pressure(res['p'], res['grid'], res['re'])
            layout.render_plot_with_caption(fig3, "图3: 压力场分布 (Pressure)", "#ffe3e3")
            
    else:
        st.info("👆 点击“开始计算”按钮查看结果")

# ==============================================================================
# 模块 3: 知识库/文章
# ==============================================================================
elif mode == "知识库/文章":
    
    if st.session_state.reading_article:
        # 阅读模式
        article = st.session_state.reading_article
        col_btn, col_txt = st.columns([1, 6])
        with col_btn:
            if st.button("⬅️ 返回", use_container_width=True):
                st.session_state.reading_article = None
                st.rerun()
        with col_txt:
            st.markdown(f"### {article['title']}")
            
        st.divider()
        reader.render_content("posts", article['file'])

    else:
        # 列表模式
        st.header("📚 知识库")
        st.divider()
        
        articles = reader.load_catalog("posts")
        if articles:
            # 修改：改为 3 列布局，更紧凑
            cols = st.columns(3)
            for i, article in enumerate(articles):
                with cols[i % 3]:
                    if layout.render_article_item(article, i):
                        st.session_state.reading_article = article
                        st.rerun()
        else:
            st.warning("暂无文章配置 (posts/catalog.json)")
