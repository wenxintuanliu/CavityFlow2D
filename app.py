import streamlit as st
import os
from core.solver import solve_cavity
from viz import plots
from ui import layout, reader  # 引入新的 reader 模块

def main():
    layout.setup_page()
    
    # 获取返回值增加了一个 selected_post
    mode, params, selected_post = layout.sidebar_navigation()
    
    # ---------------------------------------------------------
    # 模式 1: CFD 计算 (保持原样)
    # ---------------------------------------------------------
    if mode == "CFD 计算模拟":
        if params['run_btn']:
            with st.spinner("正在求解 N-S 方程..."):
                u, v, p = solve_cavity(
                    params['Re'], params['grid'], params['grid'], 
                    params['iter'], params['dt'], 1e-5, params['omega']
                )
                
                st.subheader(f"计算结果 (Re={params['Re']})")
                tab1, tab2, tab3 = st.tabs(["速度云图", "流线图", "压力场"])
                with tab1: st.pyplot(plots.plot_velocity_magnitude(u, v, params['grid'], params['Re']))
                with tab2: st.pyplot(plots.plot_streamlines(u, v, params['grid'], params['Re']))
                with tab3: st.pyplot(plots.plot_pressure(p, params['grid'], params['Re']))
        else:
            st.info("👈 请在左侧侧边栏设置参数并点击 '开始计算'")

    # ---------------------------------------------------------
    # 模式 2: 知识库 (读取 posts 文件夹)
    # ---------------------------------------------------------
    elif mode == "知识库 / 文章":
        if selected_post:
            file_path = os.path.join("posts", selected_post)
            st.subheader(f"📂 {selected_post}")
            reader.render_content(file_path)
        else:
            st.info("请在 `posts` 文件夹中添加 .md 或 .html 文件，并推送到 GitHub。")

    # ---------------------------------------------------------
    # 模式 3: 临时预览 (上传文件)
    # ---------------------------------------------------------
    elif mode == "临时文件预览":
        reader.show_file_uploader_preview()

if __name__ == "__main__":
    main()
