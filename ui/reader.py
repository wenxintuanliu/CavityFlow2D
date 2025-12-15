import streamlit as st
import os
import json
import streamlit.components.v1 as components

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

def load_file_content(file_path):
    """读取文件内容"""
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

def render_content(directory, filename):
    """渲染内容"""
    file_path = os.path.join(directory, filename)
    content = load_file_content(file_path)
    
    if content is None:
        st.error(f"❌ 无法读取文件: {filename}")
        return

    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    try:
        if ext == '.md':
            st.markdown(content, unsafe_allow_html=True)
        elif ext == '.html':
            # 修改：使用 markdown 渲染 HTML 以消除 iframe 滚动条
            # 注意：这要求 HTML 最好是片段形式（div/p等），不要包含完整的 html/body 标签
            st.markdown(content, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"渲染出错: {e}")
