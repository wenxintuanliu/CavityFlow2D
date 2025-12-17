import streamlit as st

def apply_custom_style():
    """注入自定义 CSS"""
    st.markdown("""
        <style>
        /* 0. 字体优化 */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Microsoft YaHei", sans-serif;
        }

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

        /* 3. CFD 参数按钮：零背景 + 纯黑符号风格 */
        
        /* 默认状态 */
        [data-testid="stNumberInput"] button {
            background-color: transparent !important; /* 透明背景 */
            border: 1px solid #dee2e6 !important;     /* 浅灰边框 */
            color: #000000 !important;                /* 强制符号纯黑 */
            border-radius: 4px !important;
            transition: all 0.2s ease;
        }

        /* 鼠标悬停状态 */
        [data-testid="stNumberInput"] button:hover {
            background-color: transparent !important; /* 保持透明 */
            border-color: #000000 !important;         /* 边框变黑，提示可点击 */
            color: #000000 !important;                /* 符号保持纯黑 */
            transform: translateY(-1px);              /* 微微上浮 */
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }

        /* 鼠标按下/点击状态 */
        [data-testid="stNumberInput"] button:active {
            background-color: transparent !important; /* 点击时不许变色 */
            border-color: #000000 !important;
            color: #000000 !important;                /* 点击时符号保持纯黑 */
            transform: translateY(0) scale(0.96);     /* 按压效果 */
            box-shadow: none !important;
        }
        
        /* 双重保险：强制内部 SVG 图标也是黑色 */
        [data-testid="stNumberInput"] button svg {
            fill: #000000 !important;
        }

        /* 4. 开始计算按钮 */
        [data-testid="stForm"] button {
            background: linear-gradient(135deg, #228be6 0%, #15aabf 100%);
            color: white !important;
            border: none;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 6px rgba(34, 139, 230, 0.2);
            transition: all 0.3s ease;
        }
        [data-testid="stForm"] button:hover {
            background: linear-gradient(135deg, #1c7ed6 0%, #1098ad 100%);
            box-shadow: 0 6px 12px rgba(34, 139, 230, 0.3);
            transform: translateY(-2px);
        }

        /* 5. 卡片样式优化 */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 10px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            background-color: #fff;
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.08);
            border-color: #ced4da;
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
            color: #333333;   /* 高级黑 */
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            text-align: center;
            pointer-events: none;
            background-color: transparent; /* 透明背景 */
            z-index: 100;
        }
        </style>
    """, unsafe_allow_html=True)

# 定义一组高级渐变色主题 (背景色 + 文字色)
CARD_THEMES = [
    {"bg": "linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%)", "icon": "📘"},   # 蓝紫
    {"bg": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)", "icon": "📕"},   # 红粉
    {"bg": "linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)", "icon": "📗"},   # 青绿
    {"bg": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)", "icon": "📙"},   # 橙黄
]

def render_card_standard(article, index):
    # 循环使用主题色
    theme = CARD_THEMES[index % len(CARD_THEMES)]
    tag_icon = "🏷️"
    
    # 纯 HTML 卡片渲染
    # 使用 st.markdown 渲染整个卡片，以获得完全的样式控制
    card_html = f"""
    <div style="
        background: {theme['bg']};
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        color: white;
        transition: transform 0.3s ease;
    " onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="
                background: rgba(255,255,255,0.25);
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                backdrop-filter: blur(5px);
            ">{tag_icon} {article.get('tag', 'Article')}</span>
        </div>
        <h3 style="margin: 0 0 10px 0; font-size: 1.2rem; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">{article['title']}</h3>
        <p style="font-size: 0.9rem; opacity: 0.95; margin-bottom: 15px; line-height: 1.5;">{article['summary']}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    # 按钮必须在 markdown 之外，为了布局美观，我们用一个不可见的列来占位，或者直接放按钮
    # 由于 HTML 块占据了空间，按钮会显示在卡片下方。
    # 为了让按钮看起来像在卡片里，我们可以把卡片下半部分留白，或者...
    # 实际上，混合 HTML 和 Streamlit 组件比较难对齐。
    # 方案：卡片作为背景，按钮紧随其后。为了视觉统一，我们给按钮加个样式。
    
    if st.button(f"阅读 {article['title']} ➜", key=f"read_{index}"):
        return True
    
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True) # 间距
    return False

def render_plot_with_caption(fig, caption_text, color_theme="#f8f9fa"):
    st.pyplot(fig)
    st.markdown(f"""
        <div class="plot-container">
            <span class="plot-caption" style="background-color: {color_theme};">
                {caption_text}
            </span>
        </div>
    """, unsafe_allow_html=True)
