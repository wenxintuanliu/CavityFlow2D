import streamlit as st
import os
import streamlit.components.v1 as components
import re

# -----------------------------------------------------------------------------
# 0. 核心兼容性修复：处理 Streamlit 版本差异
# -----------------------------------------------------------------------------
# 检查是否存在 st.cache_data (新版)，不存在则使用 st.cache (旧版)
if hasattr(st, 'cache_data'):
    # 新版 Streamlit (>= 1.18)
    # ttl=3600 秒 (1小时过期), max_entries=50 (防止内存溢出)
    cache_decorator = st.cache_data(show_spinner=False, max_entries=50, ttl=3600)
else:
    # 旧版 Streamlit (< 1.18)
    # allow_output_mutation=True 在旧版处理字符串/HTML内容时更稳定
    cache_decorator = st.cache(show_spinner=False, ttl=3600, allow_output_mutation=True)

# -----------------------------------------------------------------------------
# 1. 辅助函数
# -----------------------------------------------------------------------------

def list_files(directory="posts"):
    """列出文件并排序"""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError:
            return []
    # 忽略大小写排序，支持 md 和 html
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.md', '.html'))]
    files.sort(key=lambda x: x.lower()) 
    return files

# 使用刚才定义的兼容装饰器
@cache_decorator
def load_file_content(file_path):
    """读取文件内容，自动修复 Markdown 格式问题"""
    content = ""
    # 1. 读取文件 (处理多重编码)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()
        except:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()

    # 2. 自动修复 Markdown 格式问题
    # 解决 "### 标题" 紧挨着 "1. 列表" 导致渲染失败的问题
    if file_path.lower().endswith('.md'):
        # 正则：在标题行(Hexxx)和列表行(1.xxx)之间插入空行
        pattern = r'(^#{1,6} .*)\n([0-9]+\.|-|\*)'
        content = re.sub(pattern, r'\1\n\n\2', content, flags=re.MULTILINE)

    return content

# -----------------------------------------------------------------------------
# 2. 渲染逻辑
# -----------------------------------------------------------------------------

def render_content(file_path):
    if not os.path.exists(file_path):
        st.error(f"❌ 找不到文件: {file_path}")
        return

    file_name = os.path.basename(file_path)
    # 获取文件大小 (MB)
    try:
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    except:
        file_size_mb = 0

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    # 大文件提示
    if file_size_mb > 20:
        st.warning(f"⚠️ 文件较大 ({file_size_mb:.1f} MB)，渲染可能需要一点时间。")

    try:
        # 显示加载转圈
        with st.spinner(f"正在渲染 {file_name} ..."):
            content = load_file_content(file_path)
            
            if ext == '.md':
                # Markdown 渲染配置
                st.markdown(
                    f"""
                    <div class="markdown-text">
                    {content}
                    </div>
                    <style>
                        img {{max-width: 100%;}} 
                        .markdown-text {{line-height: 1.6;}}
                    </style>
                    """, 
                    unsafe_allow_html=True
                )
                
            elif ext == '.html':
                # HTML 渲染
                components.html(content, height=800, scrolling=True)
                
    except Exception as e:
        st.error(f"❌ 错误: {str(e)}")

# -----------------------------------------------------------------------------
# 3. 预览功能
# -----------------------------------------------------------------------------

def show_file_uploader_preview():
    st.info("💡 提示：此处仅供临时预览。")
    uploaded_file = st.file_uploader("文件预览", type=['md', 'html'])
    
    if uploaded_file is not None:
        try:
            content = uploaded_file.getvalue().decode("utf-8", errors='ignore')
            
            if uploaded_file.name.endswith('.md'):
                # 预览时同样应用正则修复
                pattern = r'(^#{1,6} .*)\n([0-9]+\.|-|\*)'
                content = re.sub(pattern, r'\1\n\n\2', content, flags=re.MULTILINE)
                st.markdown(content, unsafe_allow_html=True)
            else:
                components.html(content, height=800, scrolling=True)
        except Exception as e:
            st.error(f"解析失败: {e}")
