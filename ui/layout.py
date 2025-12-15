import streamlit as st

def apply_custom_style():
    """注入自定义 CSS"""
    st.markdown("""
        <style>
        /* 1. 全局设置 */
        .stApp { background-color: #ffffff; }
        footer, #MainMenu { visibility: hidden; }

        /* 2. 侧边栏按钮微调 */
        [data-testid="stSidebar"] [role="radiogroup"] > label {
            padding: 10px 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            border: 1px solid transparent;
            transition: all 0.2s;
        }
        [data-testid="stSidebar"] [role="radiogroup"] > label:hover {
            background-color: #e9ecef; /* 浅灰悬停 */
            color: #000;
        }

        /* 3. CFD 参数按钮：零背景风格 (Ghost Style) */
        /* 正常状态 */
        [data-testid="stNumberInput"] button {
            background-color: transparent !important; /* 完全透明背景 */
            border: 1px solid #dee2e6 !important;     /* 浅灰色边框 */
            color: #000000 !important;                /* 纯黑色文字 */
            border-radius: 4px !important;
            transition: all 0.2s ease;
            box-shadow: none !important;              /* 移除默认阴影 */
        }

        /* 鼠标悬停状态 - 轻微跳动效果 */
        [data-testid="stNumberInput"] button:hover {
            background-color: transparent !important;  /* 保持透明背景 */
            border-color: #495057 !important;          /* 边框变深 */
            color: #212529 !important;                /* 文字稍浅一些，创造跳动感 */
            transform: translateY(-1px);              /* 轻微上移，创造跳动感 */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important; /* 添加轻微阴影 */
        }

        /* 点击按下状态 */
        [data-testid="stNumberInput"] button:active {
            transform: translateY(0) scale(0.98);     /* 回到原位并轻微缩小 */
            background-color: #f8f9fa !important;     /* 按下时轻微灰色反馈 */
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important; /* 更小的阴影 */
        }

        /* 焦点状态 */
        [data-testid="stNumberInput"] button:focus {
            outline: none !important;                 /* 移除默认焦点轮廓 */
            border-color: #007bff !important;         /* 蓝色边框指示焦点 */
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1) !important; /* 轻微蓝色光晕 */
        }

        /* 4. 开始计算按钮 */
        [data-testid="stForm"] button {
            background: #228be6;
            color: white !important;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        [data-testid="stForm"] button:hover {
            background: #1c7ed6;
        }

        /* 5. 卡片样式优化 */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 8px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            background-color: #fff;
        }

        /* 6. 图片标题 */
        .plot-caption {
            text-align: center;
            font-size: 13px;
            font-weight: 600;
            color: #495057;
            background-color: #f8f9fa;
            padding: 4px 12px;
            border-radius: 12px;
            margin-top: -5px; 
            margin-bottom: 15px;
            border: 1px solid #dee2e6;
            display: inline-block;
        }
        .plot-container { text-align: center; }

        /* 7. 版权页脚 (高级黑，无背景) */
        .sidebar-copyright {
            position: fixed;
            bottom: 15px;
            left: 20px;
            width: 260px;
            font-size: 12px;
            font-weight: 500;
            color: #333333;   /* 高级黑 (Charcoal) */
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            text-align: center;
            pointer-events: none;
            background-color: transparent; /* 透明背景 */
            z-index: 100;
        }
        </style>
    """, unsafe_allow_html=True)

def render_card_standard(article, index):
    with st.container(border=True):
        st.markdown(f":grey-background[**{article.get('tag', 'Article')}**]") # 改为灰色背景标签，更稳重
        st.markdown(f"#### {article['title']}")
        st.caption(f"{article['summary']}")
        if st.button("阅读文章 ➜", key=f"read_{index}", use_container_width=True):
            return True
    return False

def render_plot_with_caption(fig, caption_text, color_theme="#f8f9fa"):
    st.pyplot(fig, use_container_width=True)
    st.markdown(f"""
        <div class="plot-container">
            <span class="plot-caption" style="background-color: {color_theme};">
                {caption_text}
            </span>
        </div>
    """, unsafe_allow_html=True)
