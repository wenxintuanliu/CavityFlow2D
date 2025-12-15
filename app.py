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
    st.caption("Ver 3.0 | Pro Edition")
    st.markdown("---")
    
    # 模式选择 (layout.py 已优化间距)
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
    
    # A. 渲染文字 (HTML 直接嵌入，无滚动条)
    if os.path.exists("posts/about.html"):
        reader.render_content("posts", "about.html")
    else:
        st.info("⚠️ 暂无介绍内容，请创建 posts/about.html")

    st.markdown("---")

    # B. 渲染图片 (assets/cover.jpg)
    # 需求：右侧栏正中间，只显示一张图，保持大小
    img_path = os.path.join("assets", "cover.jpg")
    
    if os.path.exists(img_path):
        st.markdown("#### 📸 可视化展示")
        
        # 使用列布局来居中: [空, 图片内容, 空]
        # 比例 1:2:1 可以让中间占据一半宽度，或者根据需要调整
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.image(img_path, caption="Lid-Driven Cavity Flow Result", use_container_width=True)
    elif os.path.exists("assets"):
        # 如果 cover.jpg 不存在，随便找一张
        images = [f for f in os.listdir("assets") if f.endswith(('.png', '.jpg'))]
        if images:
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image(os.path.join("assets", images[0]), caption=images[0], use_container_width=True)

# ==============================================================================
# 模块 2: CFD 计算模拟
# ==============================================================================
elif mode == "CFD计算模拟":
    st.session_state.reading_article = None
    st.header("🌪️ 方腔流数值模拟")
    
    # --- A. 参数设置 (使用 Form 表单) ---
    # 核心修改：使用 st.form 包裹所有输入控件
    # 这样修改参数时，页面不会立刻刷新下面的结果，只有点按钮才会提交
    with st.form("cfd_params_form"):
        st.subheader("1. 模拟参数配置")
        
        c1, c2, c3 = st.columns(3)
        with c1: re_num = st.number_input("雷诺数 (Re)", 1.0, 5000.0, 100.0, 10.0)
        with c2: grid_size = st.slider("网格密度 (Nx=Ny)", 21, 201, 41, 10)
        with c3: time_step = st.number_input("时间步长 (dt)", 0.0001, 0.1, 0.001, format="%.4f")
            
        c4, c5, c6 = st.columns(3)
        with c4: max_iter = st.number_input("最大迭代步数", 500, 20000, 2000, step=500)
        with c5: omega = st.slider("SOR 松弛因子", 1.0, 1.95, 1.8)
        with c6: st.write("") # 占位
        
        st.markdown("<br>", unsafe_allow_html=True)
        # 表单提交按钮
        submitted = st.form_submit_button("🚀 开始计算 (Start Calculation)", use_container_width=True)

    st.divider()

    # --- B. 计算逻辑 ---
    if submitted:
        with st.spinner("正在进行 N-S 方程求解..."):
            try:
                u, v, p = solve_cavity(re_num, grid_size, grid_size, max_iter, time_step, 1e-5, omega)
                # 保存结果到 Session State
                st.session_state.cfd_result = {"u": u, "v": v, "p": p, "re": re_num, "grid": grid_size}
                st.success("✅ 计算完成")
            except Exception as e:
                st.error(f"Error: {e}")

    # --- C. 结果展示 ---
    # 即使页面因为其他原因刷新，只要 session_state 里有结果，就会显示
    # 而且因为上面用了 Form，单纯调参数不会让这里闪烁
    if st.session_state.cfd_result:
        res = st.session_state.cfd_result
        st.subheader(f"2. 模拟结果可视化 (Re={res['re']})")
        
        # 3 列并排显示图片
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
    
    # 场景 3.1: 阅读详情
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
        reader.render_content("posts", article['file'])

    # 场景 3.2: 列表页
    else:
        st.header("📚 知识库")
        st.divider()
        
        articles = reader.load_catalog("posts")
        if articles:
            # 3 列布局
            cols = st.columns(3)
            for i, article in enumerate(articles):
                with cols[i % 3]:
                    # 核心修改：使用统一的卡片渲染函数
                    if layout.render_article_card_unified(article, i):
                        st.session_state.reading_article = article
                        st.rerun()
        else:
            st.warning("暂无文章配置 (posts/catalog.json)")
