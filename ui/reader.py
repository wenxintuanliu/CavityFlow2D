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
            # Markdown 依然用原生渲染
            st.markdown(content, unsafe_allow_html=True)
        elif ext == '.html':
            # 【重要修改】回归 iframe 渲染方式
            # 1. 解决源码显示问题：iframe 内部是独立浏览器环境，绝对不会显示代码。
            # 2. 解决滚动问题：scrolling=True 允许内容滚动。
            # 3. height=800：给一个足够的高度，如果内容更长则会出现滚动条。
            components.html(content, height=800, scrolling=True)
        else:
            st.text(content)
    except Exception as e:
        st.error(f"渲染出错: {e}")
