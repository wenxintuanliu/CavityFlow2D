import streamlit as st
import os
import json
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 0. 缓存设置
# -----------------------------------------------------------------------------
if hasattr(st, 'cache_data'):
    cache_decorator = st.cache_data(show_spinner=False, ttl=3600)
else:
    cache_decorator = st.cache(show_spinner=False, ttl=3600, allow_output_mutation=True)

# -----------------------------------------------------------------------------
# 1. 目录读取 (JSON驱动)
# -----------------------------------------------------------------------------
def load_catalog(directory="posts"):
    """读取 catalog.json 配置文件，返回文章列表"""
    json_path = os.path.join(directory, "catalog.json")
    if not os.path.exists(json_path):
        return []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ 目录文件解析失败 (catalog.json): {e}")
        return []

# -----------------------------------------------------------------------------
# 2. 文件读取 (防乱码核心)
# -----------------------------------------------------------------------------
@cache_decorator
def load_file_content(file_path):
    """读取文件内容，自动处理 BOM 头和首尾空格"""
    content = ""
    try:
        # 优先尝试 utf-8-sig (解决 Windows 记事本 BOM 问题)
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            # 其次尝试 GBK (解决中文旧编码)
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
        except:
            return None 

    return content.strip()

# -----------------------------------------------------------------------------
# 3. 渲染逻辑
# -----------------------------------------------------------------------------
def render_content(directory, filename):
    file_path = os.path.join(directory, filename)
    
    if not os.path.exists(file_path):
        st.error(f"❌ 找不到文件: {filename}")
        return

    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    content = load_file_content(file_path)
    
    if content is None:
        st.error(f"❌ 无法读取文件: {filename} (编码识别失败)")
        return

    try:
        if ext == '.md':
            st.markdown(content, unsafe_allow_html=True)
        elif ext == '.html':
            components.html(content, height=800, scrolling=True)
    except Exception as e:
        st.error(f"渲染出错: {e}")
