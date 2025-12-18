import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, LinearLocator, FormatStrFormatter


def plot_results(u, v, p, Re, Lx=1.0, Ly=1.0, filename=None, show=False):
    """
    绘制顶盖驱动方腔流的综合结果图 (u, v, p, Streamlines)。
    自动处理 MAC 网格到中心网格的插值。

    参数:
        u: x方向速度 (MAC网格: ny, nx+1) 或 插值后的中心网格 (ny, nx)
        v: y方向速度 (MAC网格: ny+1, nx) 或 插值后的中心网格 (ny, nx)
        p: 压力场 (ny, nx)
        Re: 雷诺数
        Lx, Ly: 区域尺寸
        filename: 保存文件名；为 None 则不保存
        show: 是否 plt.show()（Streamlit 下应为 False）
    """
    ny, nx = p.shape

    # 1. 处理网格插值 (MAC -> Center)
    # u: (ny, nx+1) -> (ny, nx)
    if u.shape == (ny, nx + 1):
        u_center = (u[:, :-1] + u[:, 1:]) / 2.0
    else:
        u_center = u

    # v: (ny+1, nx) -> (ny, nx)
    if v.shape == (ny + 1, nx):
        v_center = (v[:-1, :] + v[1:, :]) / 2.0
    else:
        v_center = v

    # 2. 生成中心网格坐标
    # 假设 p 定义在单元中心
    dx = Lx / nx
    dy = Ly / ny
    x = np.linspace(dx/2, Lx - dx/2, nx)
    y = np.linspace(dy/2, Ly - dy/2, ny)
    X, Y = np.meshgrid(x, y)

    # 3. 设置绘图风格
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.unicode_minus'] = False

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle(f'Lid-Driven Cavity Flow Results (Re={Re})', fontsize=24, fontweight='bold', y=0.96)

    # 辅助函数：坐标轴格式化
    def axis_formatter(x, pos):
        if abs(x) < 1e-9:
            return "0"
        return f"{x:.1f}"

    major_formatter = FuncFormatter(axis_formatter)

    # 辅助函数：设置子图样式
    def setup_axis(ax, title):
        ax.set_title(title, fontsize=20, fontweight='bold')
        ax.set_xlabel('x', fontsize=18, fontname='Times New Roman')
        ax.set_ylabel('y', fontsize=18, fontname='Times New Roman')
        ax.set_aspect('equal')
        ax.set_xlim(0, Lx)
        ax.set_ylim(0, Ly)

        # 设置刻度格式
        ax.xaxis.set_major_formatter(major_formatter)
        ax.yaxis.set_major_formatter(major_formatter)

        # 设置刻度字体大小
        ax.tick_params(axis='both', which='major', labelsize=16)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontname('Times New Roman')

    # 辅助函数：设置颜色条样式
    def setup_colorbar(cbar):
        # 7个标签，均匀分布
        cbar.locator = LinearLocator(numticks=7)
        cbar.formatter = FormatStrFormatter('%.1f')
        cbar.update_ticks()

        cbar.ax.tick_params(labelsize=16)
        for label in cbar.ax.get_yticklabels():
            label.set_fontname('Times New Roman')

    # --- 子图 1: u-velocity ---
    ax1 = axes[0, 0]
    levels_u = 15
    cf1 = ax1.contourf(X, Y, u_center, levels_u, cmap='jet')
    # 叠加等高线（不显示数值标签）
    ax1.contour(X, Y, u_center, levels=levels_u, colors='k', linewidths=0.6, alpha=0.6)
    setup_axis(ax1, 'u-velocity')
    cbar1 = fig.colorbar(cf1, ax=ax1, fraction=0.046, pad=0.04)
    setup_colorbar(cbar1)

    # --- 子图 2: v-velocity ---
    ax2 = axes[0, 1]
    levels_v = 15
    cf2 = ax2.contourf(X, Y, v_center, levels_v, cmap='jet')
    # 叠加等高线（不显示数值标签）
    ax2.contour(X, Y, v_center, levels=levels_v, colors='k', linewidths=0.6, alpha=0.6)
    setup_axis(ax2, 'v-velocity')
    cbar2 = fig.colorbar(cf2, ax=ax2, fraction=0.046, pad=0.04)
    setup_colorbar(cbar2)

    # --- 子图 3: Pressure ---
    ax3 = axes[1, 0]
    levels_p = 15
    cf3 = ax3.contourf(X, Y, p, levels_p, cmap='jet')
    # 叠加等高线（不显示数值标签）
    ax3.contour(X, Y, p, levels=levels_p, colors='k', linewidths=0.6, alpha=0.6)
    setup_axis(ax3, 'Pressure Field')
    cbar3 = fig.colorbar(cf3, ax=ax3, fraction=0.046, pad=0.04)
    setup_colorbar(cbar3)

    # --- 子图 4: Streamlines ---
    ax4 = axes[1, 1]
    speed = np.sqrt(u_center**2 + v_center**2)
    # 归一化线宽
    lw = 2.5 * speed / speed.max()
    st = ax4.streamplot(X, Y, u_center, v_center, color=speed, cmap='jet',
                        density=1.5, linewidth=1.0, arrowsize=1.2)
    setup_axis(ax4, 'Streamlines')
    # 添加流线速度颜色条
    cbar4 = fig.colorbar(st.lines, ax=ax4, fraction=0.046, pad=0.04)
    setup_colorbar(cbar4)

    plt.tight_layout(rect=(0, 0.03, 1, 0.95))

    if filename:
        fig.savefig(filename, dpi=300, bbox_inches='tight')

    if show:
        plt.show()

    return fig
