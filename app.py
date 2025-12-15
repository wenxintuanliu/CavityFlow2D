import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 设置页面配置
st.set_page_config(page_title="顶盖驱动方腔流 CFD", layout="wide")


# -----------------------------------------------------------------------------
# 1. 核心求解器 (集成 Streamlit 缓存和进度条)
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def solve_cavity(Re, nx, ny, max_iter, dt, tol, omega):
    """
    求解器逻辑，增加了 Streamlit 的进度条回调。
    """
    Lx, Ly = 1.0, 1.0
    dx = Lx / (nx - 1)
    dy = Ly / (ny - 1)

    # 网格初始化
    u = np.zeros((ny, nx + 1))
    v = np.zeros((ny + 1, nx))
    p = np.zeros((ny, nx))

    # 边界速度
    u_top = 1.0

    # 预计算系数
    inv_Re = 1.0 / Re
    dx2 = dx ** 2
    dy2 = dy ** 2
    inv_denom = 1.0 / (2 * (dx2 + dy2))

    # 红黑棋盘掩码 (用于 SOR)
    y_grid, x_grid = np.meshgrid(np.arange(ny), np.arange(nx), indexing='ij')
    mask_red = (y_grid + x_grid) % 2 == 0
    mask_black = (y_grid + x_grid) % 2 == 1
    mask_red_inner = mask_red[1:-1, 1:-1]
    mask_black_inner = mask_black[1:-1, 1:-1]

    # 创建一个占位符用于进度条
    progress_bar = st.progress(0, text="正在初始化计算...")
    status_text = st.empty()

    converged = False

    # 开始迭代
    for n in range(max_iter):
        un = u.copy()
        vn = v.copy()

        # --- 动量方程 (预测步) ---
        # U 动量
        un_pad = np.pad(un, ((1, 1), (0, 0)), 'edge')
        un_pad[0, :] = -un[0, :]
        un_pad[-1, :] = 2 * u_top - un[-1, :]
        u_c = un[:, 1:-1]

        diff_u = inv_Re * ((un[:, 2:] - 2 * u_c + un[:, :-2]) / dx2 +
                           (un_pad[2:, 1:-1] - 2 * u_c + un_pad[:-2, 1:-1]) / dy2)

        du2_dx = (((u_c + un[:, 2:]) / 2) ** 2 - ((u_c + un[:, :-2]) / 2) ** 2) / dx

        v_nw = vn[1:, :-1];
        v_ne = vn[1:, 1:]
        v_sw = vn[:-1, :-1];
        v_se = vn[:-1, 1:]
        v_avg_u_top = (v_ne + v_nw) / 2
        v_avg_u_bot = (v_se + v_sw) / 2
        u_avg_y_top = (un_pad[2:, 1:-1] + u_c) / 2
        u_avg_y_bot = (u_c + un_pad[:-2, 1:-1]) / 2
        duv_dy = (u_avg_y_top * v_avg_u_top - u_avg_y_bot * v_avg_u_bot) / dy

        u_star = un.copy()
        u_star[:, 1:-1] = u_c + dt * (-du2_dx - duv_dy + diff_u)

        # V 动量
        vn_pad = np.pad(vn, ((0, 0), (1, 1)), 'edge')
        vn_pad[:, 0] = -vn[:, 0];
        vn_pad[:, -1] = -vn[:, -1]
        v_c = vn[1:-1, :]

        diff_v = inv_Re * ((vn_pad[1:-1, 2:] - 2 * v_c + vn_pad[1:-1, :-2]) / dx2 +
                           (vn[2:, :] - 2 * v_c + vn[:-2, :]) / dy2)

        dv2_dy = (((v_c + vn[2:, :]) / 2) ** 2 - ((v_c + vn[:-2, :]) / 2) ** 2) / dy

        u_ne = un[1:, 1:]
        u_nw = un[1:, :-1]
        u_se = un[:-1, 1:]
        u_sw = un[:-1, :-1]
        u_avg_v_right = (u_ne + u_se) / 2
        u_avg_v_left = (u_nw + u_sw) / 2
        v_avg_x_right = (vn_pad[1:-1, 2:] + v_c) / 2
        v_avg_x_left = (vn_pad[1:-1, :-2] + v_c) / 2
        duv_dx = (v_avg_x_right * u_avg_v_right - v_avg_x_left * u_avg_v_left) / dx

        v_star = vn.copy()
        v_star[1:-1, :] = v_c + dt * (-duv_dx - dv2_dy + diff_v)

        # 边界强制
        u_star[:, 0] = 0.0;
        u_star[:, -1] = 0.0
        v_star[0, :] = 0.0;
        v_star[-1, :] = 0.0

        # --- 压力泊松方程 (SOR) ---
        div_u_star = (u_star[:, 1:] - u_star[:, :-1]) / dx + (v_star[1:, :] - v_star[:-1, :]) / dy
        b = div_u_star / dt

        for _ in range(20):  # 内部迭代减少一点以加快显示
            # Red
            p_gs_red = (dy2 * (p[1:-1, 2:] + p[1:-1, :-2]) + dx2 * (p[2:, 1:-1] + p[:-2, 1:-1]) - dx2 * dy2 * b[1:-1,
                                                                                                              1:-1]) * inv_denom
            p[1:-1, 1:-1][mask_red_inner] = (1 - omega) * p[1:-1, 1:-1][mask_red_inner] + omega * p_gs_red[
                mask_red_inner]
            # Black
            p_gs_black = (dy2 * (p[1:-1, 2:] + p[1:-1, :-2]) + dx2 * (p[2:, 1:-1] + p[:-2, 1:-1]) - dx2 * dy2 * b[1:-1,
                                                                                                                1:-1]) * inv_denom
            p[1:-1, 1:-1][mask_black_inner] = (1 - omega) * p[1:-1, 1:-1][mask_black_inner] + omega * p_gs_black[
                mask_black_inner]

            # Neumann BC
            p[:, 0] = p[:, 1];
            p[:, -1] = p[:, -2]
            p[0, :] = p[1, :];
            p[-1, :] = p[-2, :]

        # --- 速度修正 ---
        u[:, 1:-1] = u_star[:, 1:-1] - dt * (p[:, 1:] - p[:, :-1]) / dx
        v[1:-1, :] = v_star[1:-1, :] - dt * (p[1:, :] - p[:-1, :]) / dy

        u[:, 0] = 0.0;
        u[:, -1] = 0.0
        v[0, :] = 0.0;
        v[-1, :] = 0.0
        u[-1, :] = u_top

        # --- 进度更新与收敛检查 ---
        if n % 50 == 0:
            progress_bar.progress(min(n / max_iter, 1.0), text=f"迭代步骤: {n}/{max_iter}")

            err_u = np.linalg.norm(u - un) / (np.linalg.norm(un) + 1e-12)
            err_v = np.linalg.norm(v - vn) / (np.linalg.norm(vn) + 1e-12)

            if err_u < tol and err_v < tol:
                status_text.success(f"计算在第 {n} 步收敛! (误差: {max(err_u, err_v):.2e})")
                converged = True
                break

    if not converged:
        progress_bar.progress(1.0, text="迭代完成 (达到最大步数)")
        status_text.warning("达到最大迭代次数，未完全收敛。")

    # 计算中心网格结果用于绘图
    u_final = (u[:, :-1] + u[:, 1:]) / 2
    v_final = (v[:-1, :] + v[1:, :]) / 2

    return u_final, v_final, p


# -----------------------------------------------------------------------------
# 2. Streamlit 界面逻辑
# -----------------------------------------------------------------------------

st.title("🌊 Lid-Driven Cavity Flow Solver")
st.markdown("基于 **MAC 网格** 和 **有限差分法** 的顶盖驱动方腔流在线计算 (Python + Streamlit)。")

# --- 侧边栏：参数设置 ---
with st.sidebar:
    st.header("模拟参数")

    Re = st.number_input("雷诺数 (Re)", min_value=1.0, max_value=2000.0, value=100.0, step=10.0)
    grid_size = st.slider("网格密度 (Nx=Ny)", min_value=21, max_value=81, value=41, step=10)

    st.header("求解控制")
    dt = st.number_input("时间步长 (dt)", value=0.001, format="%.4f")
    max_iter = st.number_input("最大迭代步数", value=2000, step=500)
    omega = st.slider("SOR 松弛因子 (Omega)", 1.0, 1.95, 1.8)

    run_btn = st.button("🚀 开始计算", type="primary")

# --- 主逻辑 ---
if run_btn:
    with st.spinner("正在求解 N-S 方程，请稍候..."):
        # 调用求解函数
        u_res, v_res, p_res = solve_cavity(Re, grid_size, grid_size, max_iter, dt, 1e-5, omega)

        # 结果可视化
        st.divider()
        st.subheader("计算结果可视化")

        # 准备数据
        velocity_magnitude = np.sqrt(u_res ** 2 + v_res ** 2)
        x = np.linspace(0, 1, grid_size)
        y = np.linspace(0, 1, grid_size)
        X, Y = np.meshgrid(x, y)

        # 创建选项卡
        tab1, tab2, tab3 = st.tabs(["速度云图 (Speed)", "流线图 (Streamlines)", "压力场 (Pressure)"])

        with tab1:
            fig, ax = plt.subplots(figsize=(8, 6))
            c = ax.contourf(X, Y, velocity_magnitude, levels=20, cmap='jet')
            plt.colorbar(c, ax=ax, label='Velocity Magnitude')
            ax.set_title(f"Velocity Magnitude (Re={Re})")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            st.pyplot(fig)

        with tab2:
            fig, ax = plt.subplots(figsize=(8, 6))
            # 绘制流线
            strm = ax.streamplot(x, y, u_res, v_res, color=velocity_magnitude, cmap='autumn', density=1.5)
            plt.colorbar(strm.lines, ax=ax, label='Speed')
            ax.set_title(f"Streamlines (Re={Re})")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            st.pyplot(fig)

        with tab3:
            fig, ax = plt.subplots(figsize=(8, 6))
            # 压力云图
            c = ax.contourf(X, Y, p_res, levels=20, cmap='viridis')
            plt.colorbar(c, ax=ax, label='Pressure')
            ax.set_title(f"Pressure Field (Re={Re})")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            st.pyplot(fig)

else:
    st.info("👈 请在左侧侧边栏设置参数并点击 '开始计算'。")

# -----------------------------------------------------------------------------
# 3. 理论说明
# -----------------------------------------------------------------------------
with st.expander("ℹ️ 关于此求解器"):
    st.markdown("""
    *   **数值方法**: 投影法 (Projection Method) + 显式欧拉时间推进。
    *   **空间离散**: 
        *   对流项: 守恒型中心差分 (MAC网格)。
        *   扩散项: 二阶中心差分。
    *   **压力求解**: SOR (Successive Over-Relaxation) 迭代。
    *   **适用范围**: 推荐 Re < 400。高雷诺数下中心差分可能导致数值振荡。
    """)
