import streamlit as st
import os
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 0. 核心兼容性设置 (防止报错)
# -----------------------------------------------------------------------------
# 自动检测 Streamlit 版本，决定使用哪种缓存方式
if hasattr(st, 'cache_data'):
    # 新版 (Streamlit >= 1.18)
    cache_decorator = st.cache_data(show_spinner=False, ttl=3600)
else:
    # 旧版 (Streamlit < 1.18)
    cache_decorator = st.cache(show_spinner=False, ttl=3600, allow_output_mutation=True)

# -----------------------------------------------------------------------------
# 1. 文件读取 (带缓存 & 防乱码)
# -----------------------------------------------------------------------------

def list_files(directory="posts"):
    """列出目录下的 md 和 html 文件"""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError:
            return []
            
    # 获取文件并简单排序
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.md', '.html'))]
    files.sort(key=lambda x: x.lower()) 
    return files

@cache_decorator
def load_file_content(file_path):
    """只负责读取文件内容，处理 UTF-8 和 GBK 编码"""
    try:
        # 首选 UTF-8
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 备选 GBK (解决中文 Windows 文件乱码)
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except:
            return f"❌ 无法读取文件编码: {os.path.basename(file_path)}"

# -----------------------------------------------------------------------------
# 2. 渲染逻辑 (最简化)
# -----------------------------------------------------------------------------

def render_content(file_path):
    """渲染文件内容"""
    if not os.path.exists(file_path):
        st.error(f"❌ 找不到文件: {file_path}")
        return

    # 获取后缀名
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    try:
        # 读取内容 (使用上面的缓存函数)
        content = load_file_content(file_path)

        # 渲染 Markdown
        if ext == '.md':
            st.markdown(content, unsafe_allow_html=True)
            
        # 渲染 HTML
        elif ext == '.html':
            components.html(content, height=800, scrolling=True)

    except Exception as e:
        st.error(f"渲染出错: {e}")

# -----------------------------------------------------------------------------
# 3. 简单的预览功能
# -----------------------------------------------------------------------------

def show_file_uploader_preview():
    uploaded_file = st.file_uploader("文件预览 (仅临时)", type=['md', 'html'])
    
    if uploaded_file is not None:
        try:
            # 读取上传的文件
            content = uploaded_file.getvalue().decode("utf-8", errors='ignore')
            
            if uploaded_file.name.endswith('.md'):
                st.markdown(content, unsafe_allow_html=True)
            else:
                components.html(content, height=800, scrolling=True)
        except Exception:
            st.error("文件解析失败")
