import streamlit as st
import os
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 0. 核心兼容性设置
# -----------------------------------------------------------------------------
if hasattr(st, 'cache_data'):
    cache_decorator = st.cache_data(show_spinner=False, ttl=3600)
else:
    cache_decorator = st.cache(show_spinner=False, ttl=3600, allow_output_mutation=True)

# -----------------------------------------------------------------------------
# 1. 文件读取 (修复 BOM 和 空格问题)
# -----------------------------------------------------------------------------

def list_files(directory="posts"):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError:
            return []
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.md', '.html'))]
    files.sort(key=lambda x: x.lower()) 
    return files

@cache_decorator
def load_file_content(file_path):
    """读取文件内容，自动处理 BOM 头和首尾空格"""
    content = ""
    try:
        # 1. 尝试使用 utf-8-sig (专门解决 Windows 记事本保存的 BOM 问题)
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            # 2. 如果失败，尝试 GBK (解决中文乱码)
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
        except:
            # 3. 最后尝试 latin-1
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()

    # 4. 关键修正：去除首尾看不见的空白字符
    return content.strip()

# -----------------------------------------------------------------------------
# 2. 渲染逻辑 (最简模式)
# -----------------------------------------------------------------------------

def render_content(file_path):
    if not os.path.exists(file_path):
        st.error(f"❌ 找不到文件: {file_path}")
        return

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    try:
        content = load_file_content(file_path)

        if ext == '.md':
            # 渲染 Markdown
            st.markdown(content, unsafe_allow_html=True)
            
        elif ext == '.html':
            components.html(content, height=800, scrolling=True)

    except Exception as e:
        st.error(f"渲染出错: {e}")

# -----------------------------------------------------------------------------
# 3. 预览功能
# -----------------------------------------------------------------------------

def show_file_uploader_preview():
    uploaded_file = st.file_uploader("文件预览", type=['md', 'html'])
    
    if uploaded_file is not None:
        try:
            content = uploaded_file.getvalue().decode("utf-8-sig", errors='ignore') # 预览也加了 sig
            if uploaded_file.name.endswith('.md'):
                st.markdown(content, unsafe_allow_html=True)
            else:
                components.html(content, height=800, scrolling=True)
        except Exception:
            st.error("文件解析失败")
