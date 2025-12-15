import numpy as np
import streamlit as st

@st.cache_data(show_spinner=False)
def solve_cavity(Re, nx, ny, max_iter, dt, tol, omega):
    """
    MAC网格求解器 (保持物理逻辑不变)
    """
    Lx, Ly = 1.0, 1.0
    dx = Lx / (nx - 1)
    dy = Ly / (ny - 1)

    # 网格初始化
    u = np.zeros((ny, nx + 1))
    v = np.zeros((ny + 1, nx))
    p = np.zeros((ny, nx))
    
    u_top = 1.0

    # 预计算系数
    inv_Re = 1.0 / Re
    dx2 = dx ** 2
    dy2 = dy ** 2
    inv_denom = 1.0 / (2 * (dx2 + dy2))
    
    # 掩码 (SOR)
    y_grid, x_grid = np.meshgrid(np.arange(ny), np.arange(nx), indexing='ij')
    mask_red = (y_grid + x_grid) % 2 == 0
    mask_black = (y_grid + x_grid) % 2 == 1
    mask_red_inner = mask_red[1:-1, 1:-1]
    mask_black_inner = mask_black[1:-1, 1:-1]

    # Streamlit 进度条组件
    progress_bar = st.progress(0, text="正在初始化计算...")
    status_text = st.empty()
    converged = False
    
    for n in range(max_iter):
        un = u.copy()
        vn = v.copy()

        # --- A. 动量方程 ---
        un_pad = np.pad(un, ((1, 1), (0, 0)), 'edge')
        un_pad[0, :] = -un[0, :]
        un_pad[-1, :] = 2 * u_top - un[-1, :]
        u_c = un[:, 1:-1]
        
        diff_u = inv_Re * ((un[:, 2:] - 2 * u_c + un[:, :-2]) / dx2 + 
                           (un_pad[2:, 1:-1] - 2 * u_c + un_pad[:-2, 1:-1]) / dy2)
        du2_dx = (((u_c + un[:, 2:]) / 2) ** 2 - ((u_c + un[:, :-2]) / 2) ** 2) / dx
        
        v_nw = vn[1:, :-1]; v_ne = vn[1:, 1:]
        v_sw = vn[:-1, :-1]; v_se = vn[:-1, 1:]
        v_avg_u_top = (v_ne + v_nw) / 2
        v_avg_u_bot = (v_se + v_sw) / 2
        u_avg_y_top = (un_pad[2:, 1:-1] + u_c) / 2
        u_avg_y_bot = (u_c + un_pad[:-2, 1:-1]) / 2
        duv_dy = (u_avg_y_top * v_avg_u_top - u_avg_y_bot * v_avg_u_bot) / dy
        
        u_star = un.copy()
        u_star[:, 1:-1] = u_c + dt * (-du2_dx - duv_dy + diff_u)

        vn_pad = np.pad(vn, ((0, 0), (1, 1)), 'edge')
        vn_pad[:, 0] = -vn[:, 0]; vn_pad[:, -1] = -vn[:, -1]
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

        u_star[:, 0] = 0.0; u_star[:, -1] = 0.0
        v_star[0, :] = 0.0; v_star[-1, :] = 0.0

        # --- B. 压力方程 ---
        div_u_star = (u_star[:, 1:] - u_star[:, :-1]) / dx + (v_star[1:, :] - v_star[:-1, :]) / dy
        b = div_u_star / dt

        for _ in range(20):
            p_gs_red = (dy2 * (p[1:-1, 2:] + p[1:-1, :-2]) + dx2 * (p[2:, 1:-1] + p[:-2, 1:-1]) - dx2 * dy2 * b[1:-1, 1:-1]) * inv_denom
            p[1:-1, 1:-1][mask_red_inner] = (1 - omega) * p[1:-1, 1:-1][mask_red_inner] + omega * p_gs_red[mask_red_inner]
            
            p_gs_black = (dy2 * (p[1:-1, 2:] + p[1:-1, :-2]) + dx2 * (p[2:, 1:-1] + p[:-2, 1:-1]) - dx2 * dy2 * b[1:-1, 1:-1]) * inv_denom
            p[1:-1, 1:-1][mask_black_inner] = (1 - omega) * p[1:-1, 1:-1][mask_black_inner] + omega * p_gs_black[mask_black_inner]
            
            p[:, 0] = p[:, 1]; p[:, -1] = p[:, -2]
            p[0, :] = p[1, :]; p[-1, :] = p[-2, :]

        # --- C. 修正 ---
        u[:, 1:-1] = u_star[:, 1:-1] - dt * (p[:, 1:] - p[:, :-1]) / dx
        v[1:-1, :] = v_star[1:-1, :] - dt * (p[1:, :] - p[:-1, :]) / dy
        
        u[:, 0] = 0.0; u[:, -1] = 0.0
        v[0, :] = 0.0; v[-1, :] = 0.0
        u[-1, :] = u_top

        # --- D. 检查收敛 ---
        if n % 50 == 0:
            progress_bar.progress(min(n / max_iter, 1.0), text=f"迭代步骤: {n}/{max_iter}")
            err_u = np.linalg.norm(u - un) / (np.linalg.norm(un) + 1e-12)
            err_v = np.linalg.norm(v - vn) / (np.linalg.norm(vn) + 1e-12)
            if err_u < tol and err_v < tol:
                status_text.success(f"收敛于第 {n} 步 (Error: {max(err_u, err_v):.2e})")
                converged = True
                break
    
    if not converged:
        progress_bar.progress(1.0, text="迭代完成")
        status_text.warning("达到最大步数，未完全收敛")
    
    u_final = (u[:, :-1] + u[:, 1:]) / 2
    v_final = (v[:-1, :] + v[1:, :]) / 2
    
    return u_final, v_final, p
