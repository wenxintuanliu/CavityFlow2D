import streamlit as st

def apply_custom_style():
    """注入高级科学计算风格 CSS"""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=JetBrains+Mono:wght@400;700&display=swap');

        /* 1. 全局重置 */
        .stApp {
            background-color: #f8f9fa; /* 极淡的灰白，护眼 */
            font-family: 'Roboto', sans-serif;
        }
        
        h1, h2, h3 { color: #1a1a1a; letter-spacing: -0.5px; }
        
        /* 2. 侧边栏 */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e9ecef;
            box-shadow: 2px 0 10px rgba(0,0,0,0.02);
        }
        
        /* 3. 输入框优化 */
        .stNumberInput input { font-family: 'JetBrains Mono', monospace; }
        
        /* 4. 按钮样式 (主要按钮) */
        button[kind="primary"] {
            background: #228be6 !important;
            border: none !important;
            box-shadow: 0 4px 6px rgba(34, 139, 230, 0.2);
            transition: all 0.3s;
        }
        button[kind="primary"]:hover {
            background: #1c7ed6 !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(34, 139, 230, 0.3);
        }

        /* 5. 卡片效果 */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid #e9ecef;
            background: white;
            border-radius: 8px;
            padding: 20px;
        }

        /* 6. 指标 (Metric) 美化 */
        [data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace;
            color: #228be6;
            font-size: 24px !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 12px !important;
            color: #868e96;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* 7. 图表容器 */
        .plot-container {
            background: white;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #f1f3f5;
        }
        
        /* 隐藏掉不需要的 Streamlit 元素 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;} /* 隐藏顶部彩色条 */
        
        .sidebar-copyright {
            position: fixed;
            bottom: 10px;
            left: 20px;
            font-size: 11px;
            color: #adb5bd;
        }
        </style>
    """, unsafe_allow_html=True)

def render_hero_header():
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="font-size: 42px; margin-bottom: 10px; color: #111;">CFD Studio</h1>
        <p style="color: #666; font-size: 16px;">Interactive Navier-Stokes Solver</p>
    </div>
    """, unsafe_allow_html=True)

def render_article_card(article, index):
    """渲染文章卡片"""
    with st.container(border=True):
        st.markdown(f"**{article['title']}**")
        st.markdown(f"<div style='font-size:13px; color:#666; margin-bottom:10px; height:40px; overflow:hidden;'>{article['summary']}</div>", unsafe_allow_html=True)
        if st.button("Read Article", key=f"btn_{index}", use_container_width=True):
            st.session_state.reading_article = article
            st.rerun()

def render_plot_card(fig, title):
    """图表专用容器"""
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 5px;">
        <span style="font-size: 14px; font-weight: 500; color: #495057;">{title}</span>
    </div>
    """, unsafe_allow_html=True)
    st.pyplot(fig, use_container_width=True)