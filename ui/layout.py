import streamlit as st

def apply_custom_style():
    """注入现代化的自定义 CSS (Modern Scientific Dashboard Theme)"""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* 1. 全局字体与背景 */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #1e293b; 
        }
        .stApp {
            background-color: #f8fafc; /* 极淡的灰蓝色背景 */
        }
        
        /* 2. 侧边栏优化 */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            padding: 12px 16px;
            margin-bottom: 8px;
            border-radius: 8px;
            border: 1px solid transparent;
            font-weight: 500;
            color: #475569;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background-color: #f1f5f9;
            color: #0f172a;
        }
        /* 选中状态模拟 */
        [data-testid="stSidebar"] [role="radiogroup"] [data-checked="true"] {
            background-color: #eff6ff !important;
            color: #2563eb !important;
            border: 1px solid #bfdbfe !important;
        }

        /* 3. 输入组件美化 */
        [data-testid="stNumberInput"] input {
            color: #334155;
            font-weight: 600;
        }
        [data-testid="stSlider"] div[data-baseweb="slider"] div {
            background-color: #3b82f6 !important; /* 科技蓝 */
        }

        /* 4. 主按钮 (Start Calculation) */
        [data-testid="stForm"] button[kind="secondaryFormSubmit"] {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white !important;
            border: none;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
            transition: transform 0.1s, box-shadow 0.2s;
            width: 100%;
        }
        [data-testid="stForm"] button[kind="secondaryFormSubmit"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
        }
        [data-testid="stForm"] button[kind="secondaryFormSubmit"]:active {
            transform: translateY(0);
        }

        /* 5. 通用卡片样式 (Containers) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
            padding: 20px;
        }

        /* 6. 标题增强 */
        h1 { color: #0f172a; letter-spacing: -0.025em; font-weight: 800; }
        h2 { color: #1e293b; letter-spacing: -0.025em; font-weight: 700; }
        h3 { color: #334155; font-weight: 600; }
        
        /* 7. 图表标题 Caption */
        .plot-card {
            background: white;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s;
        }
        .plot-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        }
        .plot-title {
            text-align: center;
            font-size: 14px;
            font-weight: 600;
            color: #64748b;
            margin-top: 10px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* 8. 隐藏默认元素 */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        
        /* 9. 版权信息 */
        .sidebar-copyright {
            position: fixed;
            bottom: 10px;
            left: 20px;
            font-size: 11px;
            color: #94a3b8;
            width: 260px;
            text-align: center;
            pointer-events: none;
        }
        </style>
    """, unsafe_allow_html=True)

def render_hero_header():
    """首页 Hero 区域"""
    st.markdown("""
        <div style="text-align: center; padding: 40px 0 20px 0;">
            <h1 style="font-size: 3rem; margin-bottom: 10px; background: -webkit-linear-gradient(315deg, #1e293b 25%, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                CFD Studio
            </h1>
            <p style="font-size: 1.2rem; color: #64748b; max-width: 600px; margin: 0 auto;">
                交互式二维流体力学求解器 · Python 原生驱动
            </p>
        </div>
    """, unsafe_allow_html=True)

def render_card_standard(article, index):
    """文章卡片渲染"""
    # 使用 Streamlit 原生容器，但通过 CSS 增强了外观
    with st.container(border=True):
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st.markdown(f"### {article['title']}")
            st.caption(f"{article['summary']}")
            # 标签徽章
            st.markdown(f"""
                <span style="background-color: #eff6ff; color: #2563eb; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 500;">
                    {article.get('tag', 'Article')}
                </span>
            """, unsafe_allow_html=True)
        with col2:
            st.write("") 
            st.write("")
            if st.button("Read", key=f"read_{index}", use_container_width=True):
                return True
    return False

def render_plot_with_caption(fig, caption_text):
    """带样式的绘图容器"""
    st.markdown(f"""
        <div class="plot-card">
    """, unsafe_allow_html=True)
    st.pyplot(fig, use_container_width=True)
    st.markdown(f"""
            <div class="plot-title">{caption_text}</div>
        </div>
    """, unsafe_allow_html=True)