import streamlit as st

def setup_page():
    """配置页面标题和基本布局"""
    st.set_page_config(page_title="CFD 方腔流模拟", layout="wide")
    st.title("🌊 Lid-Driven Cavity Flow Solver")
    st.markdown("---")

def sidebar_navigation():
    """侧边栏导航与参数设置"""
    with st.sidebar:
        st.header("导航")
        # 允许用户切换“计算模式”或“浏览外部网页”
        mode = st.radio("选择功能", ["CFD 计算模拟", "查看参考文档/网页"])
        
        st.divider()
        
        params = {}
        if mode == "CFD 计算模拟":
            st.header("模拟参数")
            params['Re'] = st.number_input("雷诺数 (Re)", 1.0, 2000.0, 100.0, 10.0)
            params['grid'] = st.slider("网格密度 (Nx=Ny)", 21, 81, 41, 10)
            st.subheader("高级设置")
            params['dt'] = st.number_input("时间步长 (dt)", value=0.001, format="%.4f")
            params['iter'] = st.number_input("最大迭代", value=2000, step=500)
            params['omega'] = st.slider("SOR 因子", 1.0, 1.95, 1.8)
            
            params['run_btn'] = st.button("🚀 开始计算", type="primary")
        
        else:
            st.info("在此模式下，您可以查看嵌入的外部网页。")
            params = None

    return mode, params

def render_external_page():
    """嵌入外部网页的示例"""
    st.subheader("📚 参考文档 / 外部链接")
    url = st.text_input("输入网址 (需支持 iframe)", "https://wenxintuanliu.github.io/")
    try:
        # 使用 Streamlit 组件嵌入网页
        st.components.v1.iframe(src=url, height=800, scrolling=True)
    except Exception as e:
        st.error(f"无法加载网页: {e}")

def show_theory_expander():
    """显示底部的理论说明"""
    with st.expander("ℹ️ 关于此求解器 (理论背景)"):
        st.markdown("""
        *   **数值方法**: 投影法 (Projection Method)
        *   **架构**: 核心算法与前端展示分离 (Modular Design)
        *   **网格**: 交错网格 (MAC Grid)
        """)
