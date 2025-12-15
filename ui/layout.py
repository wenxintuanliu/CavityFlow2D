import streamlit as st

def apply_custom_style():
    """注入自定义 CSS，实现高级清新风格"""
    st.markdown("""
        <style>
        /* 1. 全局字体与背景微调 */
        .stApp {
            background-color: #ffffff;
        }

        /* 2. 隐藏默认页脚和汉堡菜单 */
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}

        /* 3. 侧边栏样式优化 */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa; /* 极淡灰 */
            border-right: 1px solid #e9ecef;
        }
        
        /* 4. Radio 按钮美化 (导航栏) */
        .stRadio > div {
            background-color: transparent;
            gap: 10px;
        }
        .stRadio label {
            font-weight: 500 !important;
            padding: 10px 15px;
            border-radius: 8px;
            transition: background-color 0.2s;
        }
        .stRadio label:hover {
            background-color: #e9ecef;
        }

        /* 5. 知识库卡片样式 */
        .card-container {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
            height: 100%;
            margin-bottom: 15px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card-container:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-color: #dee2e6;
        }
        .card-tag {
            display: inline-block;
            background-color: #e7f5ff;
            color: #1971c2;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .card-title {
            font-size: 18px;
            font-weight: 700;
            color: #343a40;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        .card-summary {
            font-size: 14px;
            color: #868e96;
            line-height: 1.6;
        }
        
        /* 6. 按钮美化 */
        div.stButton > button {
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_article_card(article, index):
    """
    渲染单个文章卡片
    返回: True (如果点击了按钮), False (未点击)
    """
    with st.container():
        # HTML 视觉层
        st.markdown(f"""
        <div class="card-container">
            <div class="card-tag">{article.get('tag', 'General')}</div>
            <div class="card-title">{article['title']}</div>
            <div class="card-summary">{article['summary']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 交互层：透明按钮覆盖或者下方按钮
        # 这里的 key 必须唯一，所以使用了 index
        if st.button(f"阅读 📖", key=f"read_btn_{index}", use_container_width=True):
            return True
            
    return False
