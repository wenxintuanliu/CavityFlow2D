import streamlit as st
import os
import json
import re

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

def _render_html_strict(content):
    """
    严格的 HTML 渲染模式。
    防止 Streamlit 将 HTML 误判为 Markdown 代码块。
    """
    # 1. 移除可能的 HTML 文档声明，只保留 body 内容（如果存在）
    # 简单的正则匹配，提取 body 内部
    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
    if body_match:
        content = body_match.group(1)
        
    # 2. 包裹在一个 div 中，并确保没有前导空格
    # Streamlit Markdown 如果遇到 4 个空格缩进，会变成代码块
    # 我们压缩每一行的空格，或者简单地包裹
    html_block = f"""
    <div style="font-family: sans-serif; line-height: 1.6;">
        {content}
    </div>
    """
    st.markdown(html_block, unsafe_allow_html=True)

def render_content(directory, filename):
    """通用渲染入口"""
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
            _render_html_strict(content)
        else:
            st.text(content)
    except Exception as e:
        st.error(f"渲染出错: {e}")
