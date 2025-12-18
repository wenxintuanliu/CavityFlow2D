import numpy as np
from tqdm import tqdm


def lid_driven_cavity_mac(
        Re=100, nx=60, ny=60, max_iter=20000, dt=0.001, Vtol=1e-6, Ptol=1e-6,
        pressure_solver="sor", omega=1.8,
        save_interval=None,
    progress_callback=None,
    progress_every=50,
):
    """
    MAC网格 + 有限差分法求解顶盖驱动方腔流。

    参数:
        Vtol: 速度场收敛容差 (默认 1e-5)
        Ptol: 压力泊松方程收敛容差 (默认 1e-6)
        pressure_solver: 'jacobi', 'gauss_seidel', 'sor'
        omega: 仅当 solver='sor' 时生效。推荐范围 1.7 - 1.9。
               对于 gauss_seidel，omega 会自动被视为 1.0。
        save_interval:
            - None: 不保存全历史，只在结束时保存最后一帧（最省内存，推荐）。
            - 正整数 N: 每 N 个时间步保存一次快照；并且结束时也会保存最后一帧。
        progress_callback:
            - None: 不回调。
            - Callable[[int, int, str], None]: 进度回调函数，参数为 (current_step, total_steps, message)。
              该回调应尽量轻量；用于 Streamlit 等界面进度展示。
        progress_every:
            - 回调频率，每 progress_every 步回调一次（默认 50）。
    """

    # -------------------------------------------------------------------------
    # 1. 基础设置与网格初始化
    # -------------------------------------------------------------------------
    Lx, Ly = 1.0, 1.0
    dx = Lx / nx
    dy = Ly / ny

    # MAC 网格定义
    # u: (ny, nx+1) 垂直网格面
    # v: (ny+1, nx) 水平网格面
    # p: (ny, nx)   单元中心
    u = np.zeros((ny, nx + 1))
    v = np.zeros((ny + 1, nx))
    p = np.zeros((ny, nx))

    # 边界速度
    u_top = 1.0

    # 结果容器
    u_list = []
    v_list = []
    p_list = []

    # save_interval 参数校验
    if save_interval is not None:
        try:
            save_interval = int(save_interval)
        except (TypeError, ValueError):
            raise ValueError("save_interval 必须是 None 或正整数")
        if save_interval <= 0:
            raise ValueError("save_interval 必须是 None 或正整数")

    # 预计算系数 (避免循环内重复计算)
    inv_Re = 1.0 / Re
    dx2 = dx ** 2
    dy2 = dy ** 2
    denom = 2 * (dx2 + dy2)
    inv_denom = 1.0 / denom

    # -------------------------------------------------------------------------
    # 参数稳定性检查 (CFL & Diffusion)
    # -------------------------------------------------------------------------
    u_max_est = 1.0  # 顶盖驱动速度
    # CFL 条件: dt <= dx / u
    dt_cfl = min(dx, dy) / u_max_est
    # 扩散限制: dt <= Re * dx^2 / 4
    dt_diff = 0.25 * Re * min(dx, dy) ** 2
    dt_recommended = min(dt_cfl, dt_diff)

    print(f"--- 参数检查 ---")
    print(f"网格: {nx}x{ny}, Re: {Re}")
    print(f"推荐 dt <= {dt_recommended:.5f} (CFL: {dt_cfl:.5f}, Diff: {dt_diff:.5f})")

    if dt > dt_recommended:
        print(f"警告: 当前 dt={dt} 可能导致不稳定！建议减小 dt。")
    else:
        print(f"当前 dt={dt} 满足稳定性条件。")

    if pressure_solver == "sor":
        print(f"当前 Solver 为 SOR，使用 omega={omega}。推荐范围通常在 1.7 - 1.9 之间。")

    # 准备红黑棋盘掩码 (仅用于 SOR/GS 的向量化)
    # 如果是 Jacobi，我们不会使用这些掩码
    mask_red = None
    mask_black = None
    if pressure_solver in ["sor", "gauss_seidel"]:
        y_grid, x_grid = np.meshgrid(np.arange(ny), np.arange(nx), indexing='ij')
        mask_red = (y_grid + x_grid) % 2 == 0
        mask_black = (y_grid + x_grid) % 2 == 1
        # 注意：新的 PPE 求解器将在全域求解，因此直接使用全尺寸掩码

    # 确定松弛因子
    # 如果不是 SOR，强制 omega = 1.0 (GS) 或不使用 (Jacobi)
    if pressure_solver == "gauss_seidel":
        current_omega = 1.0
    elif pressure_solver == "sor":
        current_omega = omega
    else:
        current_omega = None  # Jacobi 不使用

    print(f"开始计算: Re={Re}, Grid={nx}x{ny}, Solver={pressure_solver}")

    # progress_every 参数校验
    if progress_every is None:
        progress_every = 50
    try:
        progress_every = int(progress_every)
    except (TypeError, ValueError):
        progress_every = 50
    if progress_every <= 0:
        progress_every = 50

    # -------------------------------------------------------------------------
    # 2. 时间步迭代
    # -------------------------------------------------------------------------
    iterator = range(max_iter)
    # 若外部传入回调，一般不需要 tqdm 输出；否则保留 tqdm 的命令行体验
    if progress_callback is None:
        iterator = tqdm(iterator, desc="计算进度", unit="step")

    for n in iterator:
        un = u.copy()
        vn = v.copy()

        if progress_callback is not None and (n % progress_every == 0):
            progress_callback(n, max_iter, f"计算中... ({n}/{max_iter})")

        # ==================== A. 求解动量方程 (预测步) ====================

        # --- U 动量方程 (针对内部垂直面 u[j, i]) ---
        # 扩展边界以处理 Ghost Cells
        un_pad = np.pad(un, ((1, 1), (0, 0)), 'edge')
        un_pad[0, :] = -un[0, :]  # 下壁面无滑移
        un_pad[-1, :] = 2 * u_top - un[-1, :]  # 顶盖 Dirichlet

        u_c = un[:, 1:-1]

        # 扩散项 (Laplacian)
        diff_u = inv_Re * (
                (un[:, 2:] - 2 * u_c + un[:, :-2]) / dx2 +
                (un_pad[2:, 1:-1] - 2 * u_c + un_pad[:-2, 1:-1]) / dy2
        )

        # 对流项 (MAC格式核心：平均与差分)
        # 1. du^2/dx
        du2_dx = (((u_c + un[:, 2:]) / 2) ** 2 - ((u_c + un[:, :-2]) / 2) ** 2) / dx

        # 2. d(uv)/dy
        # 需要插值 v 到 u 的位置 (垂直边角点)
        v_nw = vn[1:, :-1]  # 左上
        v_ne = vn[1:, 1:]  # 右上
        v_sw = vn[:-1, :-1]  # 左下
        v_se = vn[:-1, 1:]  # 右下

        v_avg_u_top = (v_ne + v_nw) / 2
        v_avg_u_bot = (v_se + v_sw) / 2
        u_avg_y_top = (un_pad[2:, 1:-1] + u_c) / 2
        u_avg_y_bot = (u_c + un_pad[:-2, 1:-1]) / 2

        duv_dy = (u_avg_y_top * v_avg_u_top - u_avg_y_bot * v_avg_u_bot) / dy

        u_star = un.copy()
        u_star[:, 1:-1] = u_c + dt * (-du2_dx - duv_dy + diff_u)

        # --- V 动量方程 (针对内部水平面 v[j, i]) ---
        vn_pad = np.pad(vn, ((0, 0), (1, 1)), 'edge')
        vn_pad[:, 0] = -vn[:, 0]
        vn_pad[:, -1] = -vn[:, -1]

        v_c = vn[1:-1, :]

        # 扩散项
        diff_v = inv_Re * (
                (vn_pad[1:-1, 2:] - 2 * v_c + vn_pad[1:-1, :-2]) / dx2 +
                (vn[2:, :] - 2 * v_c + vn[:-2, :]) / dy2
        )

        # 对流项
        # 1. d(v^2)/dy
        dv2_dy = (((v_c + vn[2:, :]) / 2) ** 2 - ((v_c + vn[:-2, :]) / 2) ** 2) / dy

        # 2. d(uv)/dx
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

        # 强制中间速度边界
        u_star[:, 0] = 0.0
        u_star[:, -1] = 0.0
        v_star[0, :] = 0.0
        v_star[-1, :] = 0.0
        # ==================== B. 压力泊松方程 (PPE) ====================

        # 计算源项 b = (1/dt) * div(u*)
        div_u_star = (u_star[:, 1:] - u_star[:, :-1]) / dx + \
                     (v_star[1:, :] - v_star[:-1, :]) / dy
        b = div_u_star / dt

        # 使用 Ghost Cells 扩展 p 以处理边界条件 (Neumann BC: dp/dn = 0)
        p_pad = np.pad(p, ((1, 1), (1, 1)), 'edge')

        # 最大 PPE 迭代次数 (防止死循环)
        max_ppe_iter = 2000

        if pressure_solver == "jacobi":
            # --- 雅可比迭代 ---
            for it_ppe in range(max_ppe_iter):
                p_old_inner = p_pad[1:-1, 1:-1].copy()

                # 1. 应用 Neumann 边界条件到 Ghost Cells
                p_pad[0, 1:-1] = p_pad[1, 1:-1]   # Bottom
                p_pad[-1, 1:-1] = p_pad[-2, 1:-1] # Top
                p_pad[1:-1, 0] = p_pad[1:-1, 1]   # Left
                p_pad[1:-1, -1] = p_pad[1:-1, -2] # Right

                # 2. 更新所有流体网格 (1:-1, 1:-1)
                p_new = (dy2 * (p_pad[1:-1, 2:] + p_pad[1:-1, :-2]) +
                         dx2 * (p_pad[2:, 1:-1] + p_pad[:-2, 1:-1]) -
                         dx2 * dy2 * b) * inv_denom

                p_pad[1:-1, 1:-1] = p_new

                # 检查收敛 (每 10 步检查一次以节省开销)
                if it_ppe % 10 == 0:
                    diff = np.max(np.abs(p_new - p_old_inner))
                    if diff < Ptol:
                        break

            # 取回结果
            p = p_pad[1:-1, 1:-1]

        elif pressure_solver in ["sor", "gauss_seidel"]:
            # --- SOR / GS 迭代 (红黑排序) ---
            if mask_red is None or mask_black is None:
                raise RuntimeError("内部错误：SOR/GS 模式下未正确初始化 mask_red/mask_black")

            for it_ppe in range(max_ppe_iter):
                p_old_inner = p_pad[1:-1, 1:-1].copy()

                # 1. 应用 BCs
                p_pad[0, 1:-1] = p_pad[1, 1:-1]
                p_pad[-1, 1:-1] = p_pad[-2, 1:-1]
                p_pad[1:-1, 0] = p_pad[1:-1, 1]
                p_pad[1:-1, -1] = p_pad[1:-1, -2]

                # 2. Red Update
                p_gs = (dy2 * (p_pad[1:-1, 2:] + p_pad[1:-1, :-2]) +
                        dx2 * (p_pad[2:, 1:-1] + p_pad[:-2, 1:-1]) -
                        dx2 * dy2 * b) * inv_denom

                p_pad[1:-1, 1:-1][mask_red] = (1 - current_omega) * p_pad[1:-1, 1:-1][mask_red] + \
                                              current_omega * p_gs[mask_red]

                # 3. Black Update
                p_gs = (dy2 * (p_pad[1:-1, 2:] + p_pad[1:-1, :-2]) +
                        dx2 * (p_pad[2:, 1:-1] + p_pad[:-2, 1:-1]) -
                        dx2 * dy2 * b) * inv_denom

                p_pad[1:-1, 1:-1][mask_black] = (1 - current_omega) * p_pad[1:-1, 1:-1][mask_black] + \
                                                current_omega * p_gs[mask_black]

                # 检查收敛
                if it_ppe % 10 == 0:
                    diff = np.max(np.abs(p_pad[1:-1, 1:-1] - p_old_inner))
                    if diff < Ptol:
                        break

            # 取回结果
            p = p_pad[1:-1, 1:-1]

        # 归一化压力
        p -= np.mean(p)

        # ==================== C. 速度修正 (Projection) ====================

        # 修正 u
        u[:, 1:-1] = u_star[:, 1:-1] - dt * (p[:, 1:] - p[:, :-1]) / dx
        # 修正 v
        v[1:-1, :] = v_star[1:-1, :] - dt * (p[1:, :] - p[:-1, :]) / dy

        # 强制最终边界条件
        u[:, 0] = 0.0
        u[:, -1] = 0.0
        v[0, :] = 0.0
        v[-1, :] = 0.0
        u[-1, :] = u_top  # 恢复驱动速度

        # ==================== D. 检查收敛与数据保存 ====================

        converged = False
        if n % 100 == 0:
            # 使用相对误差
            err_u = np.linalg.norm(u - un) / (np.linalg.norm(un) + 1e-12)
            err_v = np.linalg.norm(v - vn) / (np.linalg.norm(vn) + 1e-12)

            if err_u < Vtol and err_v < Vtol:
                print(f"收敛于第 {n} 步 (Error: {max(err_u, err_v):.2e})")
                converged = True

        # 按需保存快照：save_interval=None 时不保存历史
        if save_interval is not None:
            if (n % save_interval) == 0:
                u_list.append(u.copy())
                v_list.append(v.copy())
                p_list.append(p.copy())

        if converged:
            if progress_callback is not None:
                progress_callback(n + 1, max_iter, f"已收敛，停止于第 {n + 1} 步")
            break

    else:
        print(f"达到最大迭代次数 {max_iter}，未完全收敛。")

    # 结束时保证保存最后一帧（无论是否收敛）
    u_list.append(u.copy())
    v_list.append(v.copy())
    p_list.append(p.copy())

    if progress_callback is not None:
        progress_callback(min(max_iter, n + 1), max_iter, "计算完成")


    return u_list, v_list, p_list
