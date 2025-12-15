import os
import streamlit.components.v1 as components
import re  # <--- 1. 引入正则表达式模块
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
    files = [f for f in os.listdir(directory) if f.lower().endswith(('.md', '.html'))]
    files.sort(key=lambda x: x.lower()) 
    return files
@st.cache_data(show_spinner=False, max_entries=50, ttl=3600)
def load_file_content(file_path):
    """读取文件内容，自动修复 Markdown 格式问题"""
    content = ""
    # 1. 读取文件 (处理编码)
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
    # 2. 自动修复格式问题 (针对你的问题)
    # 正则逻辑：如果发现 "### 标题" 紧接着换行后是 "1. " 或 "- " 或 "* "
    # 就在它们中间强行插入两个换行符
    if file_path.lower().endswith('.md'):
        # pattern 解释:
        # (^#{1,6} .*)  --> 捕获组1: 行首的 # 号标题
        # \n            --> 紧接着的一个换行
        # ([0-9]+\.|-|\*) --> 捕获组2: 数字列表(1.) 或 无序列表(- 或 *)
        pattern = r'(^#{1,6} .*)\n([0-9]+\.|-|\*)'
        
        # 替换为: 组1 + \n\n + 组2
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
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if file_size_mb > 20:
        st.warning(f"⚠️ 文件较大 ({file_size_mb:.1f} MB)，渲染可能需要一点时间。")
    try:
        with st.spinner(f"正在渲染 {file_name} ..."):
            content = load_file_content(file_path)
            
            if ext == '.md':
                # Latex 增强配置
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
                components.html(content, height=800, scrolling=True)
                
    except Exception as e:
        st.error(f"❌ 错误: {str(e)}")

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
