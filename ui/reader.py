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
            # 【优化】使用 st.markdown 渲染 HTML，消除滚动条并实现原生融合
            # 1. 移除 html/head/body 标签，防止样式冲突
            # 2. 将 body 样式作用域限制在局部容器中
            import re
            
            # 提取 style 内容
            style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
            style_content = style_match.group(1) if style_match else ""
            
            # 将 body 选择器替换为 .about-container，防止污染全局
            style_content = style_content.replace('body {', '.about-container {')
            style_content = style_content.replace('body{', '.about-container {')
            
            # 提取 body 内部的内容
            body_match = re.search(r'<body>(.*?)</body>', content, re.DOTALL)
            body_content = body_match.group(1) if body_match else content
            
            # 组合新的 HTML
            final_html = f"""
            <style>{style_content}</style>
            <div class="about-container">
                {body_content}
            </div>
            """
            
            st.markdown(final_html, unsafe_allow_html=True)
        else:
            st.text(content)
    except Exception as e:
        st.error(f"渲染出错: {e}")
