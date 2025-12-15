import streamlit as st

def apply_custom_style():
    """注入自定义 CSS"""
    st.markdown("""
        <style>
        /* 1. 全局与隐藏默认元素 */
        .stApp { background-color: #ffffff; }
        footer, #MainMenu { visibility: hidden; }

        /* 2. 侧边栏导航按钮优化 */
        [data-testid="stSidebar"] [role="radiogroup"] > label {
            background-color: transparent;
            border: 1px solid #e9ecef;
            margin-bottom: 12px; /* 增加间距 */
            padding: 10px 15px;
            border-radius: 8px;
            transition: all 0.3s;
        }
        [data-testid="stSidebar"] [role="radiogroup"] > label:hover {
            border-color: #339af0;
            background-color: #e7f5ff;
        }
        /* 选中状态的样式需要 Streamlit 内部类名，这里做通用增强 */

        /* 3. “开始计算”按钮 (Primary Button) 鲜艳化 */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(45deg, #228be6, #15aabf); /* 蓝青渐变 */
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.1s;
        }
        div.stButton > button[kind="primary"]:hover {
            transform: scale(1.02);
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        }

        /* 4. 知识库卡片样式 (将普通按钮伪装成卡片) */
        /* 给普通按钮增加背景色和阴影，不再是扁平的白色 */
        .article-btn-container button {
            background-color: #f8f9fa !important; /* 浅灰底 */
            border: 1px solid #dee2e6 !important;
            color: #212529 !important;
            text-align: left !important;
            padding: 20px !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
            height: 100%;
        }
        .article-btn-container button:hover {
            background-color: #fff !important;
            border-color: #339af0 !important;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
            transform: translateY(-2px);
        }
        
        /* 5. 结果图下方的标题样式 */
        .plot-caption {
            text-align: center;
            font-family: 'Helvetica', sans-serif;
            font-weight: 600;
            color: #495057;
            background-color: #f1f3f5;
            padding: 5px 10px;
            border-radius: 15px;
            margin-top: -10px; /* 紧贴图片 */
            margin-bottom: 20px;
            border: 1px solid #ced4da;
            display: inline-block;
        }
        .plot-container {
            text-align: center;
        }

        /* 6. 文章元数据 */
        .article-meta {
            font-size: 12px;
            color: #868e96;
            margin-bottom: 4px;
        }
        .article-summary {
            font-size: 13px;
            color: #666;
            margin-top: 5px;
            margin-bottom: 20px;
            padding-left: 5px;
            height: 40px; /* 固定高度防止错位 */
            overflow: hidden;
            text-overflow: ellipsis;
        }
        </style>
    """, unsafe_allow_html=True)

def render_article_item(article, index):
    """渲染知识库卡片"""
    with st.container():
        # 给按钮外层加一个特定 class 方便 CSS 定位
        st.markdown('<div class="article-btn-container">', unsafe_allow_html=True)
        
        # 标签
        st.markdown(f"<div class='article-meta'>🏷️ {article.get('tag', 'General')}</div>", unsafe_allow_html=True)
        
        # 标题 (作为按钮)
        if st.button(f"{article['title']}", key=f"art_{index}", use_container_width=True):
            st.markdown('</div>', unsafe_allow_html=True)
            return True
            
        # 摘要
        st.markdown(f"<div class='article-summary'>{article['summary']}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
            
    return False

def render_plot_with_caption(fig, caption_text, caption_color="#e7f5ff"):
    """渲染带样式的图片"""
    st.pyplot(fig, use_container_width=True)
    # 渲染美化的标题
    st.markdown(f"""
        <div class="plot-container">
            <span class="plot-caption" style="background-color: {caption_color};">
                {caption_text}
            </span>
        </div>
    """, unsafe_allow_html=True)
