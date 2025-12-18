import streamlit as st
import os
import io

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
    tag_text = article.get('tag', 'Article')
    
    # 根据标签设置不同的背景色 (淡雅色系)
    if tag_text == "理论":
        tag_style = "background: #e7f5ff; color: #1971c2;" # 浅蓝
    elif tag_text == "结果":
        tag_style = "background: #ebfbee; color: #2b8a3e;" # 浅绿
    else:
        tag_style = "background: #f1f3f5; color: #495057;" # 浅灰
    
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
                    {tag_style}
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 0.8rem;
                    font-weight: 600;
                    white-space: nowrap;
                    border: 1px solid rgba(0,0,0,0.05);
                ">{tag_icon} {tag_text}</span>
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
    # 说明：st.pyplot 往往会用 tight bbox 导出并按容器宽度缩放。
    # 当不同图的刻度/标题/色标文字宽度略有差异时，会导致“同 figsize 的图”在页面上缩放比例不同，
    # 从而出现 Streamlines 看起来略大/略小的现象。
    # 这里改为固定画布尺寸导出 PNG（不做 tight 裁剪），让四张图的像素尺寸一致，从源头消除该问题。
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches=None)
    buf.seek(0)
    st.image(buf.getvalue(), use_container_width=True)
    st.markdown(f"""
        <div class="plot-container">
            <span class="plot-caption" style="background-color: {color_theme};">
                {caption_text}
            </span>
        </div>
    """, unsafe_allow_html=True)
