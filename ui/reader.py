import streamlit as st
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
        st.error(f"❌ catalog.json 解析失败: {e}")
        return []

def load_file_content(file_path):
    """读取文件内容，处理编码"""
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
            # 核心修改：包裹一层 div 确保它被作为 HTML 块渲染
            # 这样浏览器会解析 tags 而不是显示代码
            html_block = f'<div class="custom-html-container">{content}</div>'
            st.markdown(html_block, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"渲染出错: {e}")
