import streamlit as st
from core.solver import solve_cavity
from viz import plots
from ui import layout

def main():
    # 1. 页面初始化
    layout.setup_page()
    
    # 2. 获取侧边栏输入
    mode, params = layout.sidebar_navigation()
    
    # 3. 根据模式显示内容
    if mode == "查看参考文档/网页":
        layout.render_external_page()
    
    elif mode == "CFD 计算模拟":
        # 如果点击了开始计算，或者是已经计算过有缓存的情况
        if params['run_btn']:
            with st.spinner("正在求解 N-S 方程..."):
                # 调用核心求解器
                u, v, p = solve_cavity(
                    params['Re'], params['grid'], params['grid'], 
                    params['iter'], params['dt'], 1e-5, params['omega']
                )
                
                # 结果可视化布局
                st.subheader(f"计算结果 (Re={params['Re']})")
                tab1, tab2, tab3 = st.tabs(["速度云图", "流线图", "压力场"])
                
                with tab1:
                    fig = plots.plot_velocity_magnitude(u, v, params['grid'], params['Re'])
                    st.pyplot(fig)
                
                with tab2:
                    fig = plots.plot_streamlines(u, v, params['grid'], params['Re'])
                    st.pyplot(fig)
                    
                with tab3:
                    fig = plots.plot_pressure(p, params['grid'], params['Re'])
                    st.pyplot(fig)
        else:
            st.info("👈 请在左侧设置参数并点击 '开始计算'")
            
    # 4. 底部说明
    layout.show_theory_expander()

if __name__ == "__main__":
    main()
