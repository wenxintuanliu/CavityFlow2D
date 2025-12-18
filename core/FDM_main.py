import matplotlib.pyplot as plt
import numpy as np
# 设置支持中文的字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 用于正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用于正常显示负号

# 方腔计算函数：包括边界条件，时间迭代，求解压力方程，修正步，速度边界条件
from solver import lid_driven_cavity_mac
from center_line import zxpm
from plot_flow import plot_results

def get_input(prompt, type_func, default=None):
    while True:
        if default is not None:
            user_input = input(f"{prompt} [默认: {default}]: ").strip()
            if user_input == "":
                return default
        else:
            user_input = input(f"{prompt}: ").strip()

        try:
            return type_func(user_input)
        except ValueError:
            print(f"输入无效，请输入 {type_func.__name__} 类型的值。")

print("=== 二维顶盖驱动方腔流模拟参数设置 ===")

# 1. 物理参数
Re = get_input("请输入雷诺数 Re", float, default=100.0)

# 2. 网格参数
nx = get_input("请输入 x 方向网格数 nx", int, default=60)
ny = get_input("请输入 y 方向网格数 ny", int, default=60)

# 3. 计算推荐的时间步长
Lx, Ly = 1.0, 1.0
dx = Lx / nx  # MAC 网格定义: nx 为单元数
dy = Ly / ny
u_max_est = 1.0  # 顶盖驱动速度

# CFL 条件: dt <= dx / u
dt_cfl = min(dx, dy) / u_max_est
# 扩散限制: dt <= Re * dx^2 / 4
dt_diff = 0.25 * Re * min(dx, dy) ** 2
dt_recommended = min(dt_cfl, dt_diff)

print(f"\n--- 时间步长建议 ---")
print(f"基于当前网格 ({nx}x{ny}) 和 Re={Re}:")
print(f"  CFL 限制 dt <= {dt_cfl:.6f}")
print(f"  扩散限制 dt <= {dt_diff:.6f}")
print(f"  >> 推荐 dt <= {dt_recommended:.6f}")

while True:
    dt = get_input("请输入时间步长 dt", float, default=float(f"{dt_recommended:.6f}"))
    if dt > dt_recommended:
        confirm = input(f"警告: dt={dt} 大于推荐值 {dt_recommended:.6f}，可能导致计算不稳定。是否继续？(y/n): ").strip().lower()
        if confirm == 'y':
            break
    else:
        break

# 4. 迭代参数
max_iter = get_input("请输入最大迭代步数 max_iter", int, default=20000)
Vtol = get_input("请输入速度场收敛容差 Vtol", float, default=1e-6)
Ptol = get_input("请输入压力方程收敛容差 Ptol", float, default=1e-6)

# 4.1 是否保存间隔时间步内存数据
save_interval = None
save_choice = get_input("是否希望保存间隔时间步内存数据？(y/n)", str, default="n").strip().lower()
if save_choice in ["y", "yes"]:
    save_interval = get_input("请输入保存间隔 N（每 N 步保存一次快照）", int, default=200)
else:
    save_interval = None  # 只保存最后一帧

# 5. 求解器设置
print("\n可用压力求解器: jacobi, gauss_seidel, sor")
while True:
    pressure_solver = get_input("请选择压力求解器", str, default="sor").lower()
    if pressure_solver in ["jacobi", "gauss_seidel", "sor"]:
        break
    print("无效的选择，请重新输入。")

omega = 1.8 # 默认值
if pressure_solver == "sor":
    print(f"\n--- SOR 松弛因子建议 ---")
    print("推荐范围: 1.7 - 1.9")
    omega = get_input("请输入松弛因子 omega", float, default=1.8)

print("\n=== 参数设置完成，开始计算 ===\n")

u_list, v_list, p_list = lid_driven_cavity_mac(
    Re=Re, nx=nx, ny=ny, max_iter=max_iter, dt=dt, Vtol=Vtol, Ptol=Ptol,
    pressure_solver=pressure_solver, omega=omega,
    save_interval=save_interval,
)

# ==========================================
# 后处理与绘图
# ==========================================

# 1. 生成精确的网格坐标
# x_face: (nx+1,)  网格面坐标 (0, dx, 2dx, ..., Lx)
# x_center: (nx,)  网格中心坐标 (dx/2, 3dx/2, ...)
x_face = np.linspace(0, Lx, nx + 1)
y_face = np.linspace(0, Ly, ny + 1)

x_center = (x_face[:-1] + x_face[1:]) / 2.0
y_center = (y_face[:-1] + y_face[1:]) / 2.0

# 2. 获取最后一步的结果
u_final = u_list[-1]  # (ny, nx+1)
v_final = v_list[-1]  # (ny+1, nx)
p_final = p_list[-1]  # (ny, nx)

# 3. 调用中心剖面绘图函数
print("\n正在绘制中心剖面对比图...")
zxpm(u_final, v_final, x_face, y_face, x_center, y_center, Re)

# 4. 绘制综合结果图 (u, v, p, Streamlines)
print("正在绘制综合结果图...")
plot_results(u_final, v_final, p_final, Re=Re, Lx=Lx, Ly=Ly, filename=f'cavity_flow_results_Re{Re}.png')
