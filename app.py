import streamlit as st
import os

# 1. 页面配置
st.set_page_config(page_title="CFD Studio", layout="wide")

# 懒加载：将重型库的导入移到需要的地方，或者保持核心库在顶层但优化结构
import ui.style_manager as layout
import ui.reader as reader

# 2. 注入样式
layout.apply_custom_style()

# 3. 状态管理
if 'reading_article' not in st.session_state:
    st.session_state.reading_article = None
if 'cfd_result' not in st.session_state:
    st.session_state.cfd_result = None

# ==============================================================================
# 左侧栏 (Sidebar) - 固定头部防止跳动
# ==============================================================================
with st.sidebar:
    # 头部固定区域
    with st.container():
        # 修复图片路径问题：使用绝对路径或检查存在性
        icon_url = "https://cdn-icons-png.flaticon.com/512/5758/5758248.png"
        st.image(icon_url, width=60)
        st.title("CFD Studio")
        st.caption("Ver 4.1 | Stable Release")
    
    st.markdown("---")
    
    # 导航菜单 (带图标)
    nav_options = {
        "project": "🏠 项目介绍",
        "cfd": "🌊 CFD计算模拟",
        "knowledge": "📘 知识库/文章"
    }
    
    selected_key = st.radio(
        "导航菜单", 
        options=list(nav_options.keys()),
        format_func=lambda x: nav_options[x],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # 版权页脚 (无背景，高级黑)
    st.markdown('<div class="sidebar-copyright">© 2025 chunfengfusu. Some rights reserved.</div>', unsafe_allow_html=True)

# ==============================================================================
# 模块 1: 项目介绍
# ==============================================================================
if selected_key == "project":
    st.session_state.reading_article = None
    
    st.header("📖 项目介绍")
    st.divider()
    
    # A. 渲染文字 (iframe 渲染)
    if os.path.exists("posts/about.html"):
        reader.render_content("posts", "about.html")
    else:
        st.info("ℹ️ posts/about.html 未找到")

    st.markdown("---")

    # B. 渲染图片
    # 修复：使用绝对路径确保 Streamlit 能找到文件
    img_path = os.path.abspath(os.path.join("assets", "cover.jpg"))
    if os.path.exists(img_path):
        st.markdown("#### 📸 可视化展示")
        # 1:2:1 布局
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.image(img_path, caption="Lid-Driven Cavity Flow Result")

# ==============================================================================
# 模块 2: CFD 计算模拟
# ==============================================================================
elif selected_key == "cfd":
    # 懒加载：新求解器与新绘图模块
    from core.solver import lid_driven_cavity_mac
    from viz.plot_flow import plot_pressure, plot_streamlines, plot_u_velocity, plot_v_velocity
    from viz.center_line import zxpm
    import numpy as np
    import matplotlib.pyplot as plt

    st.session_state.reading_article = None
    st.header("🌪️ 方腔流数值模拟")
    
    # A. 参数区（不放在 form 内：确保修改参数后提示/控件能实时刷新）
    st.subheader("1. 模拟参数配置")

    # 核心参数
    c1, c2, c3 = st.columns(3)
    with c1:
        re_num = st.number_input(
            "雷诺数 (Re)",
            1.0,
            10000.0,
            100.0,
            10.0,
            help="雷诺数越大，流体惯性力越强，非线性越显著。",
            key="cfd_re",
        )
    with c2:
        nx = st.number_input("网格数 nx", min_value=20, max_value=400, value=60, step=5, key="cfd_nx")
    with c3:
        ny = st.number_input("网格数 ny", min_value=20, max_value=400, value=60, step=5, key="cfd_ny")

    # 时间步长推荐（与 solver 内打印一致）
    Lx, Ly = 1.0, 1.0
    dx = Lx / int(nx)
    dy = Ly / int(ny)
    u_max_est = 1.0
    dt_cfl = min(dx, dy) / u_max_est
    dt_diff = 0.25 * float(re_num) * (min(dx, dy) ** 2)
    dt_recommended = float(min(dt_cfl, dt_diff))
    st.caption(
        f"时间步长建议：dt ≤ {dt_recommended:.6f}（CFL: {dt_cfl:.6f}，Diff: {dt_diff:.6f}）"
    )

    # 高级参数：折叠隐藏，保持界面整洁
    with st.expander("⚙️ 高级求解器设置 (Advanced Settings)", expanded=False):
        st.caption("调整以下参数以控制收敛速度和稳定性：")

        c4, c5, c6 = st.columns(3)
        with c4:
            # 1) 默认值不要用格式化截断（避免推荐值很小时变成 0 导致减号按钮直接不可用）
            # 2) 设置一个合理 step，让 +/- 按钮可用且有意义
            dt_default = float(np.clip(dt_recommended, 1e-12, 0.1))
            time_step = st.number_input(
                "时间步长 (dt)",
                min_value=1e-12,
                max_value=0.1,
                value=dt_default,
                step=1e-3,
                format="%.2e",
                key="cfd_dt",
            )
        with c5:
            max_iter = st.number_input("最大时间步数", 100, 200000, 20000, step=1000, key="cfd_max_iter")
        with c6:
            pressure_solver = st.selectbox(
                "压力方程求解器",
                options=["jacobi", "gauss_seidel", "sor"],
                index=2,
                key="cfd_pressure_solver",
            )

        c7, c8, c9 = st.columns(3)
        with c7:
            Vtol = st.number_input(
                "速度场收敛容差 Vtol",
                value=1e-6,
                step=1e-6,
                format="%.1e",
                key="cfd_vtol",
            )
        with c8:
            Ptol = st.number_input(
                "压力方程收敛容差 Ptol",
                value=1e-6,
                step=1e-6,
                format="%.1e",
                key="cfd_ptol",
            )
        with c9:
            # omega 联动逻辑：
            # - Jacobi：不显示 slider，改为提示“雅可比迭代不涉及 omega”
            # - GS：显示为 1 且灰色不可改
            # - SOR：可调
            if pressure_solver == "jacobi":
                omega = 1.0
                st.info("雅可比迭代不涉及 omega。")
            elif pressure_solver == "gauss_seidel":
                omega = st.slider("SOR 松弛因子 omega", 1.0, 1.95, 1.0, disabled=True, key="cfd_omega_gs")
            else:  # sor
                omega = st.slider("SOR 松弛因子 omega", 1.0, 1.95, 1.8, key="cfd_omega_sor")

        save_snapshots = st.checkbox("保存间隔快照（用于查看收敛过程）", value=False, key="cfd_save_snapshots")
        save_interval = None
        if save_snapshots:
            save_interval = st.number_input(
                "保存间隔 N（每 N 步保存一次）",
                10,
                10000,
                200,
                step=10,
                key="cfd_save_interval",
            )

    st.markdown("<br>", unsafe_allow_html=True)
    # 单独一个 form 只放按钮：保留你现有的按钮样式，同时不影响参数区的实时刷新
    with st.form("cfd_run_form"):
        submitted = st.form_submit_button("🚀 开始计算 (Start Calculation)", use_container_width=True)

    st.divider()

    # B. 计算逻辑
    if submitted:
        with st.spinner("正在进行 N-S 方程求解..."):
            try:
                u_list, v_list, p_list = lid_driven_cavity_mac(
                    Re=re_num,
                    nx=int(nx),
                    ny=int(ny),
                    max_iter=int(max_iter),
                    dt=float(time_step),
                    Vtol=float(Vtol),
                    Ptol=float(Ptol),
                    pressure_solver=pressure_solver,
                    omega=float(omega),
                    save_interval=save_interval,
                )

                st.session_state.cfd_result = {
                    "u_list": u_list,
                    "v_list": v_list,
                    "p_list": p_list,
                    "re": float(re_num),
                    "nx": int(nx),
                    "ny": int(ny),
                    "dt": float(time_step),
                    "pressure_solver": pressure_solver,
                    "omega": float(omega),
                    "save_interval": save_interval,
                }
                # 新结果产生后，清空旧的图像缓存，避免显示错帧/错参数
                st.session_state.pop("cfd_plot_cache", None)
                st.success("✅ 计算完成")
            except Exception as e:
                st.error(f"Error: {e}")

    # C. 结果展示
    if st.session_state.cfd_result:
        res = st.session_state.cfd_result
        st.subheader(f"2. 模拟结果可视化 (Re={res['re']})")

        u_list = res["u_list"]
        v_list = res["v_list"]
        p_list = res["p_list"]

        frame_count = len(u_list)
        if frame_count > 1:
            frame_idx = st.slider("选择查看的快照帧", 0, frame_count - 1, frame_count - 1, 1)
        else:
            frame_idx = frame_count - 1

        u = u_list[frame_idx]
        v = v_list[frame_idx]
        p = p_list[frame_idx]
        nx = res["nx"]
        ny = res["ny"]

        # 生成网格坐标（用于中心线对比）
        x_face = np.linspace(0.0, 1.0, nx + 1)
        y_face = np.linspace(0.0, 1.0, ny + 1)
        x_center = (x_face[:-1] + x_face[1:]) / 2.0
        y_center = (y_face[:-1] + y_face[1:]) / 2.0

        # 图像缓存：避免你在上方改参数时，下方四张图每次都重新生成（造成“重新加载”的感觉）
        plot_cache = st.session_state.setdefault("cfd_plot_cache", {})
        cache_base = (
            float(res["re"]),
            int(res["nx"]),
            int(res["ny"]),
            float(res["dt"]),
            str(res["pressure_solver"]),
            float(res["omega"]),
            int(frame_idx),
        )

        def _get_plot_bytes(name: str, fig_factory):
            key = cache_base + (name,)
            if key not in plot_cache:
                fig = fig_factory()
                try:
                    plot_cache[key] = layout.fig_to_png_bytes(fig)
                finally:
                    try:
                        plt.close(fig)
                    except Exception:
                        pass
            return plot_cache[key]

        # 1) 四张结果图拆开显示（每张图下方标注图名）
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            img_u = _get_plot_bytes(
                "u",
                lambda: plot_u_velocity(u, v, p, Re=res["re"], Lx=1.0, Ly=1.0, filename=None, show=False),
            )
            layout.render_plot_with_caption(image_bytes=img_u, caption_text="u-velocity", color_theme="#e7f5ff")
        with r1c2:
            img_v = _get_plot_bytes(
                "v",
                lambda: plot_v_velocity(u, v, p, Re=res["re"], Lx=1.0, Ly=1.0, filename=None, show=False),
            )
            layout.render_plot_with_caption(image_bytes=img_v, caption_text="v-velocity", color_theme="#e7f5ff")

        r2c1, r2c2 = st.columns(2)
        with r2c1:
            img_p = _get_plot_bytes(
                "p",
                lambda: plot_pressure(u, v, p, Re=res["re"], Lx=1.0, Ly=1.0, filename=None, show=False),
            )
            layout.render_plot_with_caption(image_bytes=img_p, caption_text="Pressure Field", color_theme="#e7f5ff")
        with r2c2:
            img_s = _get_plot_bytes(
                "s",
                lambda: plot_streamlines(u, v, p, Re=res["re"], Lx=1.0, Ly=1.0, filename=None, show=False),
            )
            layout.render_plot_with_caption(image_bytes=img_s, caption_text="Streamlines", color_theme="#e7f5ff")

        # 2) 中心线对比图放在四图下方，并居中显示（不全幅）
        img_center = _get_plot_bytes(
            "center",
            lambda: zxpm(
                u,
                v,
                x_face,
                y_face,
                x_center,
                y_center,
                int(res["re"]),
                filename=None,
                show=False,
            ),
        )

        c_left, c_mid, c_right = st.columns([1, 2, 1])
        with c_mid:
            layout.render_plot_with_caption(
                image_bytes=img_center,
                caption_text="中心线剖面对比（Ghia 1982）",
                color_theme="#e7f5ff",
            )
    else:
        st.info("👆 请设置参数并点击“开始计算”按钮。")

# ==============================================================================
# 模块 3: 知识库/文章
# ==============================================================================
elif selected_key == "knowledge":
    
    if st.session_state.reading_article:
        article = st.session_state.reading_article
        
        # --- 顶部导航栏布局优化 ---
        # 比例 [1, 10, 1]：确保中间列足够宽，且左右有对称的占位，实现视觉绝对居中
        col_back, col_title, col_placeholder = st.columns([1, 10, 1])
        
        with col_back:
            # 按钮填满左侧小列
            if st.button("⬅️ 返回", use_container_width=True):
                st.session_state.reading_article = None
                st.rerun()
                
        with col_title:
            # 使用 HTML 控制样式：居中对齐，深色字体
            # margin-top 用于微调，使其在垂直方向上与按钮对齐
            st.markdown(
                f"<h3 style='text-align: center; margin-top: 5px; color: #333;'>{article['title']}</h3>", 
                unsafe_allow_html=True
            )
            
        with col_placeholder:
            # 右侧空列，用于平衡左侧按钮的宽度
            st.write("") 
            
        st.divider()
        
        # 文章内容渲染
        reader.render_content("posts", article['file'])

    else:
        st.header("📚 知识库")
        st.divider()
        
        articles = reader.load_catalog("posts")
        if articles:
            cols = st.columns(3)
            for i, article in enumerate(articles):
                with cols[i % 3]:
                    if layout.render_card_standard(article, i):
                        st.session_state.reading_article = article
                        st.rerun()
        else:
            st.warning("暂无文章配置 (posts/catalog.json)")
