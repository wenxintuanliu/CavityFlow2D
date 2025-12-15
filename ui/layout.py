import streamlit as st

def apply_custom_style():
    """注入自定义 CSS"""
    st.markdown("""
        <style>
        /* 1. 全局设置 */
        .stApp { background-color: #ffffff; }
        footer, #MainMenu { visibility: hidden; }

        /* 2. 侧边栏按钮间距 */
        [data-testid="stSidebar"] [role="radiogroup"] > label {
            padding: 10px 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            border: 1px solid transparent;
            transition: all 0.2s;
        }
        [data-testid="stSidebar"] [role="radiogroup"] > label:hover {
            background-color: #f1f3f5;
            color: #228be6;
        }

        /* 3. CFD 参数按钮美化 (线框风格，去背景色) */
        /* 定位 stNumberInput 的加减号按钮 */
        [data-testid="stNumberInput"] button {
            background-color: transparent !important; /* 透明背景 */
            border: 1px solid #ced4da !important;     /* 浅灰边框 */
            color: #212529 !important;                /* 黑色加减号 (区别于白色) */
            border-radius: 4px !important;
            transition: all 0.2s ease;
        }
        /* 鼠标悬停时 */
        [data-testid="stNumberInput"] button:hover {
            color: #228be6 !important;                /* 鲜艳蓝文字 */
            border-color: #228be6 !important;         /* 鲜艳蓝边框 */
            background-color: rgba(34, 139, 230, 0.05) !important; /* 极淡的蓝色背景 */
        }
        /* 点击时 */
        [data-testid="stNumberInput"] button:active {
            transform: scale(0.95);
        }

        /* 4. 开始计算按钮 */
        [data-testid="stForm"] button {
            background: linear-gradient(90deg, #228be6, #15aabf);
            color: white !important;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }

        /* 5. 卡片样式 (配合 app.py 的 container) */
        /* 这是一个通用增强，让边框更柔和 */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px;
            border-color: #e9ecef;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            background-color: #fff;
        }

        /* 6. 图片标题样式 */
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

        /* 7. 版权页脚样式 (鲜艳高级蓝) */
        .sidebar-copyright {
            position: fixed;
            bottom: 10px;
            left: 20px;
            width: 260px;
            font-size: 12px;
            font-weight: 600; /* 加粗一点显得高级 */
            color: #2E59D9;   /* 鲜艳高级蓝 (Royal Blue/Vivid Blue) */
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            text-align: center;
            pointer-events: none;
            background-color: rgba(255,255,255,0.9); /* 防止文字重叠背景 */
            padding: 5px 0;
            z-index: 999;
        }
        </style>
    """, unsafe_allow_html=True)

def render_card_standard(article, index):
    """
    标准卡片渲染
    """
    with st.container(border=True):
        # 标签
        st.markdown(f":blue-background[**{article.get('tag', 'Article')}**]")
        # 标题
        st.markdown(f"#### {article['title']}")
        # 简介
        st.caption(f"{article['summary']}")
        
        # 按钮 (全宽)
        # key 必须唯一，防止冲突
        if st.button("Read More ➜", key=f"read_{index}", use_container_width=True):
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
