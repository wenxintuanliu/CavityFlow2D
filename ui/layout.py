import streamlit as st

def apply_custom_style():
    """注入自定义 CSS"""
    st.markdown("""
        <style>
        /* 1. 全局设置 */
        .stApp { background-color: #ffffff; }
        footer, #MainMenu { visibility: hidden; }

        /* 2. 侧边栏 */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
            border-right: 1px solid #e9ecef;
        }
        
        /* 3. 输入框优化 (CFD参数) */
        .stNumberInput > label { font-weight: 600; color: #495057; }
        
        /* 4. 知识库卡片伪装 */
        /* 我们将把 st.button 样式化为卡片标题 */
        div.stButton > button {
            text-align: left;
            border: 1px solid #e9ecef;
            background-color: #fff;
            color: #212529;
            padding: 15px 20px;
            border-radius: 8px;
            transition: all 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        div.stButton > button:hover {
            border-color: #339af0;
            color: #1c7ed6;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            background-color: #f8f9fa;
        }
        div.stButton > button:active {
            border-color: #1971c2;
            color: #1864ab;
        }

        /* 5. 摘要文字样式 */
        .article-summary {
            font-size: 14px;
            color: #868e96;
            margin-top: -10px; /* 拉近与按钮的距离 */
            margin-bottom: 20px;
            padding-left: 5px;
        }
        .article-tag {
            font-size: 12px;
            color: #adb5bd;
            margin-bottom: 5px;
            display: block;
        }
        </style>
    """, unsafe_allow_html=True)

def render_article_item(article, index):
    """
    渲染单个文章条目
    思路：直接用按钮显示标题，点击即跳转。摘要显示在按钮下方。
    """
    with st.container():
        # 显示标签
        st.markdown(f"<span class='article-tag'>🏷️ {article.get('tag', 'General')}</span>", unsafe_allow_html=True)
        
        # 1. 标题作为按钮 (全宽)
        # 技巧：label 直接放标题，去掉之前的“阅读”字样
        if st.button(f"📄 {article['title']}", key=f"art_{index}", use_container_width=True):
            return True
            
        # 2. 摘要显示为普通文本 (不可点，仅展示)
        st.markdown(f"<div class='article-summary'>{article['summary']}</div>", unsafe_allow_html=True)
            
    return False
