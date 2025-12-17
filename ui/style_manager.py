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
    # 循环使用主题色
    theme = CARD_THEMES[index % len(CARD_THEMES)]
    tag_icon = "🏷️"
    
    # 使用 st.container(border=True) 确保按钮在卡片内部
    # 我们通过 CSS (knowledge.css) 来美化这个容器
    # 为了实现“高级感”，我们在容器内部使用 markdown 渲染一个彩色头部
    
    with st.container(border=True):
        # 1. 彩色头部 (模拟卡片背景的一部分)
        st.markdown(f"""
            <div style="
                background: {theme['bg']};
                margin: -16px -16px 10px -16px; /* 抵消 padding */
                padding: 15px 20px;
                color: white;
                border-radius: 10px 10px 0 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 1.1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                        {theme['icon']} {article['title']}
                    </span>
                    <span style="
                        background: rgba(255,255,255,0.25);
                        padding: 2px 8px;
                        border-radius: 12px;
                        font-size: 0.8rem;
                        backdrop-filter: blur(4px);
                    ">{article.get('tag', 'Article')}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 2. 摘要内容 (在白色背景上，易读)
        st.caption(f"{article['summary']}")
        
        # 3. 按钮 (现在在卡片内部)
        if st.button(f"阅读文章 ➜", key=f"read_{index}", use_container_width=True):
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
