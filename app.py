import streamlit as st
import os

# 必须是第一个 Streamlit 命令
st.set_page_config(
    page_title="CFD 方腔流 Studio", 
    layout="wide",
    initial_sidebar_state="expanded"
)

from core.solver import solve_cavity
from viz import plots
from ui import layout, reader

# 1. 注入 CSS 样式
layout.apply_custom_style()

# 2. 初始化 Session State (用于记录文章阅读状态)
if 'reading_article' not in st.session_state:
    st.session_state.reading_article = None

# ==============================================================================
# 侧边栏：全局导航与参数
# ==============================================================================
with st.sidebar:
    st.title("🌊 CFD Studio")
    st.caption("Lid-Driven Cavity Flow Analysis")
    st.markdown("---")
    
    # 模式选择 (去掉了临时文件预览)
    mode = st.radio(
        "导航模式", 
        ["CFD计算模拟", "知识库/文章"], 
        label_visibility="collapsed"
    )
    
    st.markdown("---")

    # 定义 CFD 参数字典 (仅在 CFD 模式下显示)
    params = {}
    run_btn = False
    
    if mode == "CFD计算模拟":
        st.subheader("⚙️ 模拟参数")
        params['Re'] = st.number_input("雷诺数 (Re)", 1.0, 5000.0, 100.0, 10.0)
        params['grid'] = st.slider("网格密度 (Nx=Ny)", 21, 121, 41, 10)
        
        with st.expander("🛠️ 高级设置"):
            params['dt'] = st.number_input("时间步长", 0.0001, 0.1, 0.001, format="%.4f")
            params['iter'] = st.number_input("最大迭代步", 500, 10000, 2000, step=500)
            params['omega'] = st.slider("SOR 松弛因子", 1.0, 1.95, 1.8)
            
        st.markdown("<br>", unsafe_allow_html=True)
        run_btn = st.button("🚀 开始计算", type="primary", use_container_width=True)

    else:
        # 知识库模式下的侧边栏信息
        st.info("💡 在 catalog.json 中配置文章信息。")
        if st.session_state.reading_article:
            if st.button("⬅️ 返回文章列表", use_container_width=True):
                st.session_state.reading_article = None
                st.rerun()

# ==============================================================================
# 主界面逻辑
# ==============================================================================

# --- 场景 A: CFD 计算模拟 ---
if mode == "CFD计算模拟":
    # 切换回此模式时，重置阅读状态
    st.session_state.reading_article = None
    
    st.header(f"🖥️ 方腔流数值模拟 (Re={params.get('Re', 100)})")
    
    # 1. 如果点击了运行按钮，执行计算
    if run_btn:
        with st.spinner("正在求解 Navier-Stokes 方程..."):
            try:
                # 调用你的求解器
                u, v, p = solve_cavity(
                    params['Re'], params['grid'], params['grid'], 
                    params['iter'], params['dt'], 1e-5, params['omega']
                )
                
                # 展示结果
                st.success("计算完成！")
                tab1, tab2, tab3 = st.tabs(["🌪️ 速度云图", "〰️ 流线图", "🌡️ 压力场"])
                with tab1: st.pyplot(plots.plot_velocity_magnitude(u, v, params['grid'], params['Re']))
                with tab2: st.pyplot(plots.plot_streamlines(u, v, params['grid'], params['Re']))
                with tab3: st.pyplot(plots.plot_pressure(p, params['grid'], params['Re']))
                
            except Exception as e:
                st.error(f"计算发生错误: {e}")

    # 2. 如果没开始计算，显示 About 页和项目介绍
    else:
        # 渲染 About HTML
        if os.path.exists("posts/about.html"):
            st.markdown("### 项目介绍")
            reader.render_content("posts", "about.html")
        else:
            st.info("👋 欢迎使用！请点击左侧 **'开始计算'** 按钮运行模拟。")
            
        # 渲染静态图片 (如果 assets 文件夹下有图片)
        # 这里假设你可能会放一个示意图
        example_img_path = os.path.join("assets", "intro.png") # 示例文件名
        if os.path.exists(example_img_path):
            st.image(example_img_path, caption="Lid-Driven Cavity Flow 示意图", use_column_width=True)


# --- 场景 B: 知识库/文章 ---
elif mode == "知识库/文章":
    
    # 子场景 B1: 阅读详情页
    if st.session_state.reading_article:
        article = st.session_state.reading_article
        st.header(article['title'])
        st.caption(f"标签: {article.get('tag', '无')} | 文件: {article['file']}")
        st.divider()
        
        # 渲染正文
        reader.render_content("posts", article['file'])
        
    # 子场景 B2: 文章卡片列表页
    else:
        st.header("📚 知识库")
        st.markdown("浏览 CFD 理论推导与案例分析报告。")
        st.divider()
        
        # 读取配置
        articles = reader.load_catalog("posts")
        
        if not articles:
            st.warning("⚠️ 未找到文章配置。请在 `posts/catalog.json` 中添加内容。")
        else:
            # 3列布局
            cols = st.columns(3)
            for i, article in enumerate(articles):
                with cols[i % 3]:
                    # 渲染卡片，检测点击
                    if layout.render_article_card(article, i):
                        st.session_state.reading_article = article
                        st.rerun() # 立即刷新进入详情页
