import streamlit as st
import streamlit.components.v1 as components
import os
import json

def load_catalog(directory="posts"):
    """读取 catalog.json 配置文件"""
    json_path = os.path.join(directory, "catalog.json")
    if not os.path.exists(json_path):
        return []
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ Error loading catalog: {e}")
        return []

def load_file_content(file_path):
    """读取文件内容，包含简单的编码处理"""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return f.read().strip()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read().strip()
        except:
            return None 

def render_content(directory, filename):
    """渲染内容"""
    file_path = os.path.join(directory, filename)
    content = load_file_content(file_path)
    
    if content is None:
        st.error(f"❌ File not found: {filename}")
        return

    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext == '.md':
        st.markdown(content, unsafe_allow_html=True)
    elif ext == '.html':
        # 使用 iframe 渲染 HTML，高度稍微增加
        components.html(content, height=800, scrolling=True)
    else:
        st.text(content)