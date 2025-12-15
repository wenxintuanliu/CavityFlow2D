import streamlit as st
import os
import json
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 1. 目录读取
# -----------------------------------------------------------------------------
def load_catalog(directory="posts"):
    """读取 catalog.json 配置文件"""
    json_path = os.path.join(directory, "catalog.json")
    if not os.path.exists(json_path):
        return []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ catalog.json 解析失败: {e}")
        return []

# -----------------------------------------------------------------------------
# 2. 文件读取 (处理编码)
# -----------------------------------------------------------------------------
# 移除 cache，开发阶段方便调试，上线可加回 @st.cache_data
def load_file_content(file_path):
    """读取文件内容，自动处理 BOM"""
    if not os.path.exists(file_path):
        return None

    content = ""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
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
    
    # 获取内容
    content = load_file_content(file_path)
    
    if content is None:
        st.error(f"❌ 无法读取文件: {filename} (请检查路径或编码)")
        return

    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    try:
        if ext == '.md':
            st.markdown(content, unsafe_allow_html=True)
        elif ext == '.html':
            # 增加高度，确保内容显示全
            components.html(content, height=800, scrolling=True)
    except Exception as e:
        st.error(f"渲染出错: {e}")
