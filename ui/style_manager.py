import streamlit as st
import os

def load_css(filename):
    """读取 CSS 文件内容"""
    # 假设 CSS 文件位于 ui/layout/ 目录下
    css_path = os.path.join(os.path.dirname(__file__), "layout", filename)
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def apply_custom_style():
    """注入自定义 CSS"""
    # 加载所有 CSS 模块
    global_css = load_css("global.css")
    home_css = load_css("home.css")
    sim_css = load_css("simulation.css")
    know_css = load_css("knowledge.css")
    
    st.markdown(f"""
        <style>
        {global_css}
        {home_css}
        {sim_css}
        {know_css}
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
    # 简约风格：无背景色头部，强调文字清晰度
    tag_icon = "🏷️"
    
    with st.container(border=True):
        # 1. 头部：标题与标签
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                <h3 style="
                    margin: 0; 
                    font-size: 1.2rem; 
                    color: #1a1a1a; /* 深黑色标题 */
                    font-weight: 700;
                ">{article['title']}</h3>
                <span style="
                    background: #f1f3f5;
                    color: #495057;
                    padding: 4px 10px;
                    border-radius: 6px;
                    font-size: 0.8rem;
                    font-weight: 600;
                    white-space: nowrap;
                ">{tag_icon} {article.get('tag', 'Article')}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # 2. 摘要内容 (加深颜色)
        st.markdown(f"""
            <p style="
                font-size: 0.95rem; 
                color: #343a40; /* 深灰色正文 */
                line-height: 1.6;
                margin-bottom: 15px;
            ">{article['summary']}</p>
        """, unsafe_allow_html=True)
        
        # 3. 按钮 (在卡片内部)
        if st.button(f"阅读文章 ➜", key=f"read_{index}"):
            return True
            
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
