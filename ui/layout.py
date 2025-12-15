import streamlit as st
import os

def setup_page():
    st.set_page_config(page_title="CFD 方腔流 & 知识库", layout="wide")
    st.title("🌊 Lid-Driven Cavity Flow Studio")
    st.markdown("---")

def sidebar_navigation():
    with st.sidebar:
        st.header("功能导航")
        # 增加了 '知识库 / 文章' 选项
        mode = st.radio("选择模式", ["CFD 计算模拟", "知识库 / 文章", "临时文件预览"])
        
        st.divider()
        
        params = {}
        selected_post = None

        # --- 模式 1: 计算 ---
        if mode == "CFD 计算模拟":
            st.header("模拟参数")
            params['Re'] = st.number_input("雷诺数 (Re)", 1.0, 5000.0, 100.0, 10.0)
            params['grid'] = st.slider("网格密度 (Nx=Ny)", 21, 121, 41, 10)
            st.subheader("高级设置")
            params['dt'] = st.number_input("时间步长", 0.001, format="%.4f")
            params['iter'] = st.number_input("最大迭代", 2000, step=500)
            params['omega'] = st.slider("SOR 因子", 1.0, 1.95, 1.8)
            params['run_btn'] = st.button("🚀 开始计算", type="primary")

        # --- 模式 2: 文章列表 ---
        elif mode == "知识库 / 文章":
            st.header("文章列表")
            # 动态读取 posts 文件夹下的文件
            post_files = [f for f in os.listdir("posts") if f.endswith(('.md', '.html'))] if os.path.exists("posts") else []
            
            if post_files:
                selected_post = st.selectbox("选择文章阅读", post_files)
            else:
                st.warning("posts 文件夹为空")
        
        # --- 模式 3: 临时上传 ---
        elif mode == "临时文件预览":
            st.markdown("用于快速查看本地的 Markdown 或 HTML 导出报告。")

    return mode, params, selected_post
