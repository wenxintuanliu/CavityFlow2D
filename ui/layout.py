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
            margin-bottom: 12px;
            border-radius: 8px;
            background-color: transparent;
            border: 1px solid #e9ecef;
            transition: all 0.3s;
        }
        [data-testid="stSidebar"] [role="radiogroup"] > label:hover {
            border-color: #339af0;
            background-color: #f8f9fa;
        }

        /* 3. CFD 参数输入框加减号美化 (去填充，改线框) */
        [data-testid="stNumberInput"] button {
            background-color: transparent !important; /* 去掉背景色 */
            border: 1px solid #ced4da !important;     /* 加灰色边框 */
            color: #495057 !important;                /* 深灰字 */
            transition: all 0.2s;
        }
        [data-testid="stNumberInput"] button:hover {
            border-color: #339af0 !important;         /* 悬停变蓝 */
            color: #228be6 !important;
            background-color: #e7f5ff !important;
        }
        [data-testid="stNumberInput"] button:active {
            background-color: #d0ebff !important;
        }

        /* 4. “开始计算”按钮 (提交按钮) 保持鲜艳 */
        [data-testid="stForm"] button {
            background: linear-gradient(90deg, #228be6, #1098ad);
            color: white !important;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        [data-testid="stForm"] button:hover {
            box-shadow: 0 4px 12px rgba(34, 139, 230, 0.3);
            transform: translateY(-1px);
        }

        /* 5. 高级卡片交互技术 (HTML视觉 + 按钮交互) */
        /* 视觉层：定义卡片的样子 */
        .card-visual {
            height: 200px; /* 固定高度，确保布局对齐 */
            padding: 20px;
            border: 1px solid #dee2e6;
            border-radius: 12px;
            background-color: #f8f9fa;
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: all 0.3s;
        }
        
        /* 交互层：定义按钮覆盖在视觉层上面 */
        .card-overlay-btn {
            margin-top: -215px !important; /* 关键：负边距把按钮拉上去覆盖住视觉层 */
            height: 215px !important;      /* 高度和视觉层一致 */
            opacity: 0 !important;         /* 关键：完全透明 */
            width: 100% !important;
            z-index: 10;
            cursor: pointer;
        }
        
        /* 鼠标悬停时的视觉反馈 (通过兄弟选择器比较难做，这里简单处理) */
        /* 由于按钮在上面，鼠标悬停实际上是悬停在按钮上，我们很难改变下面div的样式 */
        /* 这是一个折衷，保持静态美观 */

        .card-tag {
            font-size: 12px;
            color: #ffffff;
            background-color: #339af0;
            padding: 4px 8px;
            border-radius: 4px;
            align-self: flex-start;
            margin-bottom: 12px;
            font-weight: 600;
        }
        .card-title {
            font-size: 18px;
            font-weight: 700;
            color: #212529;
            margin-bottom: 8px;
            line-height: 1.4;
            /* 限制标题行数 */
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .card-summary {
            font-size: 14px;
            color: #868e96;
            line-height: 1.5;
            /* 限制简介行数 */
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        /* 6. 图片标题样式 */
        .plot-caption {
            text-align: center;
            font-size: 14px;
            font-weight: 600;
            color: #495057;
            background-color: #f8f9fa;
            padding: 5px 15px;
            border-radius: 15px;
            margin-top: -10px; 
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
            display: inline-block;
        }
        .plot-container { text-align: center; }

        /* 7. 版权页脚样式 */
        .sidebar-copyright {
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 260px; /* 侧边栏宽度 */
            font-size: 12px;
            color: #adb5bd;
            font-family: sans-serif;
            text-align: center;
            pointer-events: none; /* 防止遮挡 */
        }
        </style>
    """, unsafe_allow_html=True)

def render_article_card_advanced(article, index):
    """
    渲染高级卡片：
    1. 使用 HTML 渲染出漂亮的、有区分度的视觉层 (Tag, Title, Summary)。
    2. 使用一个透明的 Button 覆盖在上面，实现点击交互。
    """
    # 1. 视觉层 (HTML)
    html_content = f"""
    <div class="card-visual">
        <div class="card-tag">{article.get('tag', 'Article')}</div>
        <div class="card-title">{article['title']}</div>
        <div class="card-summary">{article['summary']}</div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    
    # 2. 交互层 (透明按钮)
    # 这里的 key 必须唯一。按钮文字为空，因为不可见。
    # 增加 custom_class 供调试，实际通过 CSS .card-overlay-btn 控制
    clicked = st.button("Read", key=f"card_btn_{index}", use_container_width=True)
    
    # 注入 CSS 使得这个按钮上浮并透明
    # 注意：Streamlit 的 st.button 无法直接接受 class，我们需要依赖 CSS 选择器技巧
    # 或者我们使用 st.markdown 注入一段针对该按钮 ID 的 style，但这太复杂。
    # 这里我们依赖 layout.py 中的全局 CSS: .stButton > button
    # 为了只影响这里的按钮，我们必须依赖特定的结构。
    
    # *修正方案*：Streamlit 原生无法给特定按钮加 class。
    # 这里的技巧是：利用 CSS 的层叠特性。我们在 app.py 的 columns 里调用这个函数。
    # 为了让全局 CSS .card-overlay-btn 生效，我们需要在 button 周围包一个 div 吗？不行。
    # 我们只能通过 JavaScript 或者非常具体的 CSS hack。
    
    # *最终稳定方案*：
    # 既然 CSS 难以精确定位单个按钮，我们把样式写在 style 标签里紧跟按钮
    # 利用 Streamlit 渲染顺序，给所有在这个函数里生成的按钮加上负边距。
    st.markdown("""
        <style>
        div[data-testid="stVerticalBlock"] > div > div > div > div > div > button {
             /* 这是一个风险较大的选择器，但在标准布局中通常有效 */
        }
        /* 更稳妥的方式：给所有文字为 "Read" 的按钮施加魔法 (用户看不见文字因为透明) */
        div.stButton > button:first-child {
            /* 这里会影响所有按钮，危险 */
        }
        </style>
    """, unsafe_allow_html=True)
    
    # === 重新调整策略 ===
    # 上面的 CSS Hack 太不稳定。
    # 既然用户需要“有区分度”，最稳妥且美观的方案是：
    # 使用 st.container(border=True) + Markdown + 底部普通按钮
    # 这是 Streamlit 官方推荐的做法。完全透明覆盖虽然酷，但维护性极差。
    # 下面是修改后的代码，不使用透明覆盖，而是使用标准的卡片容器。
    pass # 这一行只是为了逻辑连续，下面才是真正的返回逻辑

def render_card_standard(article, index):
    """
    稳健的高级卡片渲染方案
    """
    # 使用带边框的容器作为卡片主体
    with st.container(border=True):
        # 标签 (使用 Markdown 颜色)
        st.markdown(f":blue-background[{article.get('tag', 'General')}]")
        
        # 标题 (加大加粗)
        st.markdown(f"#### {article['title']}")
        
        # 简介 (灰色小字)
        st.caption(f"{article['summary']}")
        
        # 按钮 (放在卡片底部，全宽)
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
