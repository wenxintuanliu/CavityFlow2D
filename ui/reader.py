import streamlit as st
import os
import streamlit.components.v1 as components

# -----------------------------------------------------------------------------
# 1. 辅助函数：文件列表与读取
# -----------------------------------------------------------------------------

def list_files(directory="posts"):
    """
    列出指定目录下的 md 和 html 文件，并按文件名排序
    """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError:
            st.error(f"无法创建目录: {directory}")
            return []
    
    # 获取文件并排序 (忽略大小写排序)
    files = [
        f for f in os.listdir(directory) 
        if f.lower().endswith(('.md', '.html'))
    ]
    files.sort(key=lambda x: x.lower()) 
    return files

@st.cache_data(show_spinner=False, max_entries=50, ttl=3600)
def load_file_content(file_path):
    """
    读取文件内容，带缓存控制和编码自动回退。
    max_entries=50: 最多缓存50个文件的内容，防止内存爆炸
    ttl=3600: 缓存有效期1小时，方便你更新文章后能看到变化
    """
    # 尝试 UTF-8 (标准)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # 如果失败，尝试 GBK (中文 Windows 常见)
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except Exception:
            # 最后尝试 Latin-1 (保证不报错，但可能乱码)
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()

# -----------------------------------------------------------------------------
# 2. 核心渲染逻辑
# -----------------------------------------------------------------------------

def render_content(file_path):
    """根据文件后缀渲染内容，带加载提示与异常处理"""
    if not os.path.exists(file_path):
        st.error(f"❌ 找不到文件: {file_path}")
        return

    file_name = os.path.basename(file_path)
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    # 安全检查：如果文件大于 20MB，给予警告
    if file_size_mb > 20:
        st.warning(f"⚠️ 注意：此文件较大 ({file_size_mb:.1f} MB)，浏览器渲染可能需要几秒钟，请耐心等待。")

    try:
        # 使用 spinner 包裹读取和渲染过程
        with st.spinner(f"正在加载 {file_name} ..."):
            
            # 1. 读取数据 (命中缓存则瞬间完成)
            content = load_file_content(file_path)
            
            # 2. 渲染 Markdown
            if ext == '.md':
                # 添加样式优化，防止图片过大溢出
                st.markdown(
                    f"""
                    <div style="word-wrap: break-word;">
                        {content}
                    </div>
                    <style>img {{max-width: 100%;}}</style>
                    """, 
                    unsafe_allow_html=True
                )
                
            # 3. 渲染 HTML
            elif ext == '.html':
                # HTML 组件是 iframe，渲染非常大的 HTML 可能会让浏览器卡顿
                components.html(content, height=800, scrolling=True)
                
    except Exception as e:
        st.error(f"❌ 渲染文件时发生错误: {str(e)}")

# -----------------------------------------------------------------------------
# 3. 临时预览功能
# -----------------------------------------------------------------------------

def show_file_uploader_preview():
    """提供一个临时上传预览的功能"""
    st.info("💡 提示：此处仅供临时预览，刷新即消失。永久展示请上传至 GitHub posts 目录。")
    
    uploaded_file = st.file_uploader("拖拽文件到此处预览", type=['md', 'html'])
    
    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_ext = os.path.splitext(file_name)[1].lower()
        
        st.divider()
        st.caption(f"正在预览: {file_name}")

        try:
            # 读取二进制流并解码，处理编码问题
            bytes_data = uploaded_file.getvalue()
            content = None
            
            # 尝试解码
            for encoding in ['utf-8', 'gbk', 'latin-1']:
                try:
                    content = bytes_data.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                st.error("无法识别文件编码，请确保文件是 UTF-8 格式。")
                return

            # 渲染逻辑
            if file_ext == '.md':
                st.markdown(content, unsafe_allow_html=True)
            elif file_ext == '.html':
                components.html(content, height=800, scrolling=True)
                
        except Exception as e:
            st.error(f"预览失败: {e}")
