import streamlit as st

def apply_custom_style():
    """注入自定义 CSS"""
    st.markdown("""
        <style>
        /* 1. 全局设置 */
        .stApp { background-color: #ffffff; }
        footer, #MainMenu { visibility: hidden; }

        /* 2. 侧边栏按钮间距优化 */
        [data-testid="stSidebar"] [role="radiogroup"] > label {
            padding: 12px 15px;
            margin-bottom: 15px; /* 增加按钮之间的距离 */
            border-radius: 8px;
            background-color: transparent;
            border: 1px solid #e9ecef;
            transition: all 0.3s;
        }
        [data-testid="stSidebar"] [role="radiogroup"] > label:hover {
            border-color: #339af0;
            background-color: #f1f3f5;
        }

        /* 3. “开始计算”按钮 (Form Submit) 鲜艳化 */
        [data-testid="stForm"] button {
            background: linear-gradient(90deg, #228be6, #1098ad);
            color: white !important;
            border: none;
            font-weight: bold;
            font-size: 16px;
            padding: 0.5rem 1rem;
            transition: transform 0.1s;
        }
        [data-testid="stForm"] button:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(34, 139, 230, 0.3);
        }

        /* 4. 全能卡片样式 (将 st.button 改造为卡片) */
        /* 关键：允许按钮内部文本换行 (white-space: pre-wrap) */
        .article-card-btn button {
            white-space: pre-wrap !important; 
            height: auto !important;
            min-height: 160px !important; /* 固定卡片高度 */
            width: 100% !important;
            text-align: left !important;
            align-items: flex-start !important;
            display: block !important;
            
            background-color: #f8f9fa !important;
            border: 1px solid #dee2e6 !important;
            border-radius: 12px !important;
            color: #212529 !important;
            padding: 20px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        .article-card-btn button:hover {
            border-color: #339af0 !important;
            transform: translateY(-5px) !important;
            box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important;
            background-color: #fff !important;
        }
        
        /* 隐藏按钮点击后的默认红框 */
        .article-card-btn button:focus {
            outline: none !important;
            border-color: #339af0 !important;
        }

        /* 5. 图片下方标题样式 */
        .plot-caption {
            text-align: center;
            font-size: 14px;
            font-weight: 600;
            color: #495057;
            background-color: #f8f9fa;
            padding: 8px 15px;
            border-radius: 20px;
            margin-top: -10px; 
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
            display: inline-block;
        }
        .plot-container { text-align: center; }
        </style>
    """, unsafe_allow_html=True)

def render_article_card_unified(article, index):
    """
    渲染统一的卡片。
    使用一个大按钮包含所有信息。
    """
    # 构造卡片显示的文本内容
    # 注意：Streamlit 按钮文本无法使用 Markdown，只能纯文本
    # 我们用 emoji 和 换行符来模拟排版
    tag = f"🏷️ {article.get('tag', 'General')}"
    title = f"{article['title']}"
    summary = f"{article['summary']}"
    
    # 组合文本：
    # 第一行：标签
    # 第二行：标题 (前后加换行拉开距离)
    # 第三行：简介
    button_text = f"{tag}\n\n★ {title}\n\n{summary}"
    
    # 增加一个 CSS 类包裹
    st.markdown('<div class="article-card-btn">', unsafe_allow_html=True)
    
    clicked = st.button(button_text, key=f"card_{index}", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return clicked

def render_plot_with_caption(fig, caption_text, color_theme="#f8f9fa"):
    """渲染带样式的图片"""
    st.pyplot(fig, use_container_width=True)
    st.markdown(f"""
        <div class="plot-container">
            <span class="plot-caption" style="background-color: {color_theme};">
                {caption_text}
            </span>
        </div>
    """, unsafe_allow_html=True)
