import streamlit as st
import os

# 必须是第一行
st.set_page_config(page_title="CFD Studio", layout="wide")

from core.solver import solve_cavity
from viz import plots
from ui import layout, reader

# 1. 注入样式
layout.apply_custom_style()

# 2. 状态初始化
if 'reading_article' not in st.session_state:
    st.session_state.reading_article = None
if 'cfd_result' not in st.session_state:
    st.session_state.cfd_result = None # 用于存储计算结果，防止刷新丢失

# ==============================================================================
# 左侧栏：纯净导航
# ==============================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/5758/5758248.png", width=60) # 示例Logo
    st.title("CFD Studio")
    st.caption("方腔流模拟与分析平台")
    st.markdown("---")
    
    # 模式选择 (三大模块并列)
    mode = st.radio(
        "应用导航", 
        ["项目介绍", "CFD计算模拟", "知识库/文章"], 
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("Made with ❤️ by Streamlit")

# ==============================================================================
# 模块 1: 项目介绍 (独立模块)
# ==============================================================================
if mode == "项目介绍":
    # 离开文章模式
    st.session_state.reading_article = None
    
    st.header("📖 项目介绍")
    st.divider()
    
    # 1. 优先渲染 about.html
    if os.path.exists("posts/about.html"):
        reader.render_content("posts", "about.html")
    else:
        st.info("⚠️ 请在 posts/ 目录下创建 about.html 以显示介绍内容。")

    # 2. 渲染 assets 图片 (作为补充)
    # 遍历 assets 文件夹下的所有图片并展示
    if os.path.exists("assets"):
        images = [f for f in os.listdir("assets") if f.endswith(('.png', '.jpg', '.jpeg'))]
        if images:
            st.markdown("#### 📸 项目展示")
            cols = st.columns(min(3, len(images))) # 最多3列
            for idx, img_name in enumerate(images):
                with cols[idx % 3]:
                    st.image(os.path.join("assets", img_name), caption=img_name, use_container_width=True)

# ==============================================================================
# 模块 2: CFD 计算模拟 (参数在主界面)
# ==============================================================================
elif mode == "CFD计算模拟":
    st.session_state.reading_article = None
    st.header("🌪️ 方腔流数值模拟")
    
    # --- A. 参数设置区域 (主界面) ---
    with st.container():
        st.subheader("1. 参数设置")
        
        # 第一行参数
        c1, c2, c3 = st.columns(3)
        with c1:
            re_num = st.number_input("雷诺数 (Re)", 1.0, 5000.0, 100.0, 10.0, help="决定流体惯性力与粘性力的比值")
        with c2:
            grid_size = st.slider("网格密度 (Nx=Ny)", 21, 201, 41, 10, help="网格越密计算越慢，但精度越高")
        with c3:
            time_step = st.number_input("时间步长 (dt)", 0.0001, 0.1, 0.001, format="%.4f")
            
        # 第二行参数
        c4, c5, c6 = st.columns(3)
        with c4:
            max_iter = st.number_input("最大迭代步数", 500, 20000, 2000, step=500)
        with c5:
            omega = st.slider("SOR 松弛因子", 1.0, 1.95, 1.8, help="过大可能导致发散")
        with c6:
            # 占位，让布局对齐
            st.empty()
            
        # 开始计算按钮 (全宽强调)
        st.markdown("<br>", unsafe_allow_html=True)
        start_btn = st.button("🚀 开始计算 / 更新参数", type="primary", use_container_width=True)

    st.divider()

    # --- B. 计算逻辑与结果展示 ---
    if start_btn:
        with st.spinner(f"正在求解 Re={re_num}, Grid={grid_size}x{grid_size}..."):
            try:
                # 调用求解器
                u, v, p = solve_cavity(re_num, grid_size, grid_size, max_iter, time_step, 1e-5, omega)
                
                # 将结果存入 Session State (虽然这里每次点击都重新算，但如果有复杂交互需要存)
                st.session_state.cfd_result = {
                    "u": u, "v": v, "p": p, 
                    "re": re_num, "grid": grid_size
                }
                st.success("✅ 计算完成！")
            except Exception as e:
                st.error(f"计算出错: {e}")

    # --- C. 结果显示 (如果存有结果) ---
    if st.session_state.cfd_result:
        res = st.session_state.cfd_result
        st.subheader(f"2. 模拟结果 (Re={res['re']})")
        
        tab1, tab2, tab3 = st.tabs(["速度云图", "流线图", "压力场"])
        
        # 注意：这里需要传入 result 中的参数
        with tab1: st.pyplot(plots.plot_velocity_magnitude(res['u'], res['v'], res['grid'], res['re']))
        with tab2: st.pyplot(plots.plot_streamlines(res['u'], res['v'], res['grid'], res['re']))
        with tab3: st.pyplot(plots.plot_pressure(res['p'], res['grid'], res['re']))
    
    else:
        st.info("👆 请调整上方参数并点击“开始计算”以查看结果。")

# ==============================================================================
# 模块 3: 知识库/文章
# ==============================================================================
elif mode == "知识库/文章":
    
    # 场景 3.1: 阅读详情
    if st.session_state.reading_article:
        article = st.session_state.reading_article
        
        # 顶部导航栏
        col_back, col_title = st.columns([1, 5])
        with col_back:
            if st.button("⬅️ 返回列表", use_container_width=True):
                st.session_state.reading_article = None
                st.rerun()
        with col_title:
            st.markdown(f"### {article['title']}")
        
        st.divider()
        reader.render_content("posts", article['file'])

    # 场景 3.2: 文章列表
    else:
        st.header("📚 知识库")
        st.caption("点击下方卡片阅读文章")
        st.divider()
        
        articles = reader.load_catalog("posts")
        
        if not articles:
            st.warning("⚠️ 暂无文章，请配置 posts/catalog.json")
        else:
            # 双列布局 (比三列更宽，适合做标题按钮)
            cols = st.columns(2) 
            for i, article in enumerate(articles):
                with cols[i % 2]:
                    # 渲染列表项
                    if layout.render_article_item(article, i):
                        st.session_state.reading_article = article
                        st.rerun()
