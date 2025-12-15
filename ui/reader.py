import streamlit as st
import os
import streamlit.components.v1 as components

def list_files(directory="posts"):
    """列出指定目录下的 md 和 html 文件"""
    if not os.path.exists(directory):
        os.makedirs(directory) # 如果不存在则创建
        return []
    
    files = [f for f in os.listdir(directory) if f.endswith(('.md', '.html'))]
    return files

def render_content(file_path):
    """根据文件后缀渲染内容"""
    _, ext = os.path.splitext(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if ext == '.md':
            # 渲染 Markdown
            st.markdown(content, unsafe_allow_html=True)
        elif ext == '.html':
            # 渲染 HTML (使用 iframe 组件，高度可自适应或固定)
            # scrolling=True 允许 HTML 内部滚动
            components.html(content, height=800, scrolling=True)
            
    except Exception as e:
        st.error(f"读取文件失败: {e}")

def show_file_uploader_preview():
    """提供一个临时上传预览的功能"""
    st.info("💡 提示：此处上传的文件仅供临时预览，刷新页面后会消失。若要永久展示，请将文件上传至 GitHub 的 posts 文件夹。")
    uploaded_file = st.file_uploader("上传 .md 或 .html 文件预览", type=['md', 'html'])
    
    if uploaded_file is not None:
        file_ext = os.path.splitext(uploaded_file.name)[1]
        
        # 读取二进制并解码
        content = uploaded_file.getvalue().decode("utf-8")
        
        st.divider()
        st.subheader(f"📄 预览: {uploaded_file.name}")
        
        if file_ext == '.md':
            st.markdown(content, unsafe_allow_html=True)
        elif file_ext == '.html':
            components.html(content, height=800, scrolling=True)
