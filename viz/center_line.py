import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def zxpm(u, v, x_face, y_face, x_center, y_center, target_Re, filename=None, show=False):
    """
    绘制中心剖面图，对比 Ghia (1982) 基准数据。

    参数:
        u: 原始 u 速度场 (ny, nx+1)
        v: 原始 v 速度场 (ny+1, nx)
        x_face, y_face: 网格线坐标向量 (1D array)
        x_center, y_center: 单元中心坐标向量 (1D array)
        target_Re: 雷诺数
    """
    # ==========================================
    # 1. Ghia (1982) 基准数据 (Re=100, 400, 1000, 3200, 5000, 7500, 10000)
    # ==========================================
    ghia_data = {
        100: {
            'y_u': [1.0000, 0.9766, 0.9688, 0.9609, 0.9531, 0.8516, 0.7344, 0.6172, 0.5000, 0.4531, 0.2813, 0.1719, 0.1016, 0.0703, 0.0625, 0.0547, 0.0000],
            'u':   [1.0000, 0.84123, 0.78871, 0.73722, 0.68717, 0.23151, 0.00332, -0.13641, -0.20581, -0.21090, -0.15662, -0.10150, -0.06434, -0.04775, -0.04192, -0.03717, 0.00000],
            'x_v': [1.0000, 0.9688, 0.9609, 0.9531, 0.9453, 0.9063, 0.8594, 0.8047, 0.5000, 0.2344, 0.2266, 0.1563, 0.0938, 0.0781, 0.0703, 0.0625, 0.0000],
            'v':   [0.0000, -0.05906, -0.07391, -0.08864, -0.10313, -0.16914, -0.22445, -0.24533, 0.05454, 0.17527, 0.17507, 0.16077, 0.12317, 0.10890, 0.10091, 0.09233, 0.00000]
        },
        400: {
            'y_u': [1.0000, 0.9766, 0.9688, 0.9609, 0.9531, 0.8516, 0.7344, 0.6172, 0.5000, 0.4531, 0.2813, 0.1719, 0.1016, 0.0703, 0.0625, 0.0547, 0.0000],
            'u':   [1.0000, 0.75837, 0.68439, 0.61756, 0.55892, 0.29093, 0.16256, 0.02135, -0.11477, -0.17119, -0.32726, -0.24299, -0.14612, -0.10338, -0.09266, -0.08186, 0.00000],
            'x_v': [1.0000, 0.9688, 0.9609, 0.9531, 0.9453, 0.9063, 0.8594, 0.8047, 0.5000, 0.2344, 0.2266, 0.1563, 0.0938, 0.0781, 0.0703, 0.0625, 0.0000],
            'v':   [0.0000, -0.12146, -0.15663, -0.19254, -0.22847, -0.23827, -0.44993, -0.38598, 0.05186, 0.30174, 0.30203, 0.28124, 0.22965, 0.20920, 0.19713, 0.18360, 0.00000]
        },
        1000: {
            'y_u': [1.0000, 0.9766, 0.9688, 0.9609, 0.9531, 0.8516, 0.7344, 0.6172, 0.5000, 0.4531, 0.2813, 0.1719, 0.1016, 0.0703, 0.0625, 0.0547, 0.0000],
            'u':   [1.0000, 0.65928, 0.57492, 0.51117, 0.46604, 0.33304, 0.18719, 0.05702, -0.06080, -0.10648, -0.27805, -0.38289, -0.29730, -0.22220, -0.20196, -0.18109, 0.00000],
            'x_v': [1.0000, 0.9688, 0.9609, 0.9531, 0.9453, 0.9063, 0.8594, 0.8047, 0.5000, 0.2344, 0.2266, 0.1563, 0.0938, 0.0781, 0.0703, 0.0625, 0.0000],
            'v':   [0.0000, -0.21388, -0.27669, -0.33714, -0.39188, -0.51550, -0.42665, -0.31966, 0.02526, 0.32235, 0.33075, 0.37095, 0.32627, 0.30353, 0.29012, 0.27485, 0.00000]
        },
        3200: {
            # Table I: u-velocity along vertical line (x=0.5)
            'y_u': [1.0000, 0.9766, 0.9688, 0.9609, 0.9531, 0.8516, 0.7344, 0.6172, 0.5000, 0.4531, 0.2813, 0.1719,
                    0.1016, 0.0703, 0.0625, 0.0547, 0.0000],
            'u': [1.0000, 0.53236, 0.48296, 0.46547, 0.46101, 0.34682, 0.19791, 0.07156, -0.04272, -0.086636, -0.24427,
                  -0.34323, -0.41933, -0.37827, -0.35344, -0.32407, 0.00000],
            # Table II: v-velocity along horizontal line (y=0.5)
            'x_v': [1.0000, 0.9688, 0.9609, 0.9531, 0.9453, 0.9063, 0.8594, 0.8047, 0.5000, 0.2344, 0.2266, 0.1563,
                    0.0938, 0.0781, 0.0703, 0.0625, 0.0000],
            'v': [0.0000, -0.39017, -0.47425, -0.52357, -0.54053, -0.44307, -0.37401, -0.31184, 0.00999, 0.28188,
                  0.29030, 0.37119, 0.42768, 0.41906, 0.40917, 0.39560, 0.00000]
        },
        5000: {
            # Table I: u-velocity
            'y_u': [1.0000, 0.9766, 0.9688, 0.9609, 0.9531, 0.8516, 0.7344, 0.6172, 0.5000, 0.4531, 0.2813, 0.1719,
                    0.1016, 0.0703, 0.0625, 0.0547, 0.0000],
            'u': [1.0000, 0.48223, 0.46120, 0.45992, 0.46036, 0.33556, 0.20087, 0.08183, -0.03039, -0.07404, -0.22855,
                  -0.33050, -0.40435, -0.43643, -0.42901, -0.41165, 0.00000],
            # Table II: v-velocity
            'x_v': [1.0000, 0.9688, 0.9609, 0.9531, 0.9453, 0.9063, 0.8594, 0.8047, 0.5000, 0.2344, 0.2266, 0.1563,
                    0.0938, 0.0781, 0.0703, 0.0625, 0.0000],
            'v': [0.0000, -0.49774, -0.55069, -0.55408, -0.52876, -0.41442, -0.36214, -0.30018, 0.00945, 0.27280,
                  0.28066, 0.35368, 0.42951, 0.43648, 0.43329, 0.42447, 0.00000]
        },
        7500: {
            # Table I: u-velocity
            'y_u': [1.0000, 0.9766, 0.9688, 0.9609, 0.9531, 0.8516, 0.7344, 0.6172, 0.5000, 0.4531, 0.2813, 0.1719,
                    0.1016, 0.0703, 0.0625, 0.0547, 0.0000],
            'u': [1.0000, 0.47244, 0.47048, 0.47323, 0.47167, 0.34228, 0.20591, 0.08342, -0.03800, -0.07503, -0.23176,
                  -0.32393, -0.38324, -0.43025, -0.43590, -0.43154, 0.00000],
            # Table II: v-velocity
            'x_v': [1.0000, 0.9688, 0.9609, 0.9531, 0.9453, 0.9063, 0.8594, 0.8047, 0.5000, 0.2344, 0.2266, 0.1563,
                    0.0938, 0.0781, 0.0703, 0.0625, 0.0000],
            'v': [0.0000, -0.53858, -0.55216, -0.52347, -0.48590, -0.41050, -0.36213, -0.30448, 0.00824, 0.27348,
                  0.28117, 0.35060, 0.41824, 0.43564, 0.44030, 0.43979, 0.00000]
        },
        10000: {
            # Table I: u-velocity
            'y_u': [1.0000, 0.9766, 0.9688, 0.9609, 0.9531, 0.8516, 0.7344, 0.6172, 0.5000, 0.4531, 0.2813, 0.1719,
                    0.1016, 0.0703, 0.0625, 0.0547, 0.0000],
            'u': [1.0000, 0.47221, 0.47783, 0.48070, 0.47804, 0.34635, 0.20673, 0.08344, 0.03111, -0.07540, -0.23186,
                  -0.32709, -0.38000, -0.41657, -0.42537, -0.42735, 0.00000],
            # Table II: v-velocity
            'x_v': [1.0000, 0.9688, 0.9609, 0.9531, 0.9453, 0.9063, 0.8594, 0.8047, 0.5000, 0.2344, 0.2266, 0.1563,
                    0.0938, 0.0781, 0.0703, 0.0625, 0.0000],
            'v': [0.0000, -0.54302, -0.52987, -0.49099, -0.45863, -0.41496, -0.36737, -0.30719, 0.00831, 0.27224,
                  0.28003, 0.35070, 0.41487, 0.43124, 0.43733, 0.43983, 0.00000]
        }
    }


    if target_Re in ghia_data:
        print(f"\n--- Re={target_Re} 在 Ghia (1982) 基准数据范围内 ---")
        print(f"正在绘制与基准数据的对比图...")
    else:
        print(f"\n Re={target_Re} 不在 Ghia (1982) 基准数据 (100, 400, 1000, 3200, 5000, 7500, 10000) 中。")
        print(f"将仅绘制模拟结果，不进行基准对比。")

    # ==========================================
    # 2. 数据提取 (基于精确坐标)
    # ==========================================

    # 1. 提取垂直中心线上的 u (x = 0.5)
    # u 的 x 坐标定义在 x_face 上
    idx_x_mid = (np.abs(x_face - 0.5)).argmin()
    u_vertical = u[:, idx_x_mid]
    # u 的高度坐标是 y_center (因为 u 定义在垂直面上，y方向是中心)
    y_coords = y_center

    # 2. 提取水平中心线上的 v (y = 0.5)
    # v 的 y 坐标定义在 y_face 上
    idx_y_mid = (np.abs(y_face - 0.5)).argmin()
    v_horizontal = v[idx_y_mid, :]
    # v 的宽度坐标是 x_center (因为 v 定义在水平面上，x方向是中心)
    x_coords = x_center

    # ==========================================
    # 3. 绘图
    # ==========================================
    c1 = '#1f77b4'  # u速度颜色（蓝色）
    c2 = '#d62728'  # v速度颜色（红色）
    fontsize = 24
    marker_size = 60

    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 16

    # 创建画布
    width, height = 22, 22
    fig = plt.figure(figsize=(width/2.54, height/2.54))

    # 主轴：左y轴，下x轴
    ax = fig.add_subplot(111, label="1")
    # 副轴：右y轴，上x轴
    ax2 = fig.add_subplot(111, label="2", frame_on=False)

    # -------------------------------------------------------
    # 绘制 Ghia 基准数据 (散点图)
    # -------------------------------------------------------
    ghia_handle_u = None
    ghia_handle_v = None

    if target_Re in ghia_data:
        g = ghia_data[target_Re]
        ghia_handle_u = ax.scatter(g['u'], g['y_u'], s=marker_size, facecolors='none',
                                   edgecolors=c1, linewidth=1.5, zorder=10, label=f'Ghia Re={target_Re}')
        ghia_handle_v = ax2.scatter(g['x_v'], g['v'], s=marker_size, facecolors='none',
                                    edgecolors=c2, linewidth=1.5, zorder=10, label=f'Ghia Re={target_Re}')

    # -------------------------------------------------------
    # 绘制 模拟结果 (实线)
    # -------------------------------------------------------
    line_handle_u, = ax.plot(u_vertical, y_coords, color=c1, linewidth=2.0, label=f'Present (u)')
    line_handle_v, = ax2.plot(x_coords, v_horizontal, color=c2, linewidth=2.0, label=f'Present (v)')

    # 调整副轴
    ax2.xaxis.tick_top()
    ax2.yaxis.tick_right()
    ax2.xaxis.set_label_position('top')
    ax2.yaxis.set_label_position('right')

    # 坐标轴标签
    ax.set_xlabel("u-velocity", color=c1, fontsize=fontsize, fontweight='bold')
    ax.set_ylabel("y", color=c1, fontsize=fontsize, fontweight='bold')
    ax2.set_xlabel('x', color=c2, fontsize=fontsize, fontweight='bold')
    ax2.set_ylabel('v-velocity', color=c2, fontsize=fontsize, fontweight='bold')

    # 颜色设置
    ax.tick_params(axis='x', colors=c1, labelsize=fontsize-4)
    ax.tick_params(axis='y', colors=c1, labelsize=fontsize-4)
    ax2.tick_params(axis='x', colors=c2, labelsize=fontsize-4)
    ax2.tick_params(axis='y', colors=c2, labelsize=fontsize-4)

    ax.spines["left"].set_color(c1)
    ax.spines["bottom"].set_color(c1)
    ax.spines["left"].set_linewidth(2)
    ax.spines["bottom"].set_linewidth(2)

    ax.spines["right"].set_color(c2)
    ax.spines["top"].set_color(c2)
    ax2.spines["right"].set_color(c2)
    ax2.spines["top"].set_color(c2)
    ax2.spines["right"].set_linewidth(2)
    ax2.spines["top"].set_linewidth(2)

    # 范围设置
    ax.set_xlim(-1, 1.0)
    ax.set_ylim(0, 1)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(-1, 1)

    # 辅助线
    ax.axhline(y=0.5, color='gray', linestyle=':', linewidth=1.0, alpha=0.5)
    ax2.axvline(x=0.5, color='gray', linestyle=':', linewidth=1.0, alpha=0.5)

    # 刻度格式
    formatter = FuncFormatter(lambda x, _: f"{x:.1f}")
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax2.xaxis.set_major_formatter(formatter)
    ax2.yaxis.set_major_formatter(formatter)

    # 图例合并
    handles = [line_handle_u, ghia_handle_u] if ghia_handle_u else [line_handle_u]
    labels = [h.get_label() for h in handles]
    ax.legend(
        handles,
        labels,
        loc='upper left',
        bbox_to_anchor=(0.02, 0.98),
        fontsize=10,
        title="Vertical Centerline",
        title_fontsize=10,
        frameon=True,
        framealpha=0.85,
    )

    handles2 = [line_handle_v, ghia_handle_v] if ghia_handle_v else [line_handle_v]
    labels2 = [h.get_label() for h in handles2]
    ax2.legend(
        handles2,
        labels2,
        loc='lower right',
        bbox_to_anchor=(0.98, 0.02),
        fontsize=10,
        title="Horizontal Centerline",
        title_fontsize=10,
        frameon=True,
        framealpha=0.85,
    )

    # 标题
    #plt.title(f'Lid-Driven Cavity Flow (Re = {target_Re})', fontsize=fontsize, y=1.08)

    fig.tight_layout()
    if filename:
        fig.savefig(filename, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    return fig
