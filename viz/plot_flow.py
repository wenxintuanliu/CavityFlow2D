import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, LinearLocator, FormatStrFormatter


def _prepare_center_fields(u, v, p, Lx=1.0, Ly=1.0):
    ny, nx = p.shape

    # 1) MAC -> Center
    if u.shape == (ny, nx + 1):
        u_center = (u[:, :-1] + u[:, 1:]) / 2.0
    else:
        u_center = u

    if v.shape == (ny + 1, nx):
        v_center = (v[:-1, :] + v[1:, :]) / 2.0
    else:
        v_center = v

    # 2) Center coordinates
    dx = Lx / nx
    dy = Ly / ny
    x = np.linspace(dx / 2, Lx - dx / 2, nx)
    y = np.linspace(dy / 2, Ly - dy / 2, ny)
    X, Y = np.meshgrid(x, y)

    return X, Y, u_center, v_center


def _setup_axis(ax, Lx, Ly, title):
    # 坐标轴格式化
    def axis_formatter(x, _pos):
        if abs(x) < 1e-9:
            return "0"
        return f"{x:.1f}"

    major_formatter = FuncFormatter(axis_formatter)

    ax.set_title(title, fontsize=18, fontweight='bold')
    ax.set_xlabel('x', fontsize=14, fontname='Times New Roman')
    ax.set_ylabel('y', fontsize=14, fontname='Times New Roman')
    ax.set_aspect('equal')
    ax.set_xlim(0, Lx)
    ax.set_ylim(0, Ly)
    ax.xaxis.set_major_formatter(major_formatter)
    ax.yaxis.set_major_formatter(major_formatter)
    ax.tick_params(axis='both', which='major', labelsize=12)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname('Times New Roman')


def _setup_colorbar(cbar):
    cbar.locator = LinearLocator(numticks=7)
    cbar.formatter = FormatStrFormatter('%.1f')
    cbar.update_ticks()
    cbar.ax.tick_params(labelsize=12)
    for label in cbar.ax.get_yticklabels():
        label.set_fontname('Times New Roman')


def plot_u_velocity(u, v, p, Re, Lx=1.0, Ly=1.0, levels=15, filename=None, show=False):
    X, Y, u_center, _v_center = _prepare_center_fields(u, v, p, Lx=Lx, Ly=Ly)

    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(1, 1, figsize=(6.5, 5.5), constrained_layout=True)
    cf = ax.contourf(X, Y, u_center, levels, cmap='jet')
    ax.contour(X, Y, u_center, levels=levels, colors='k', linewidths=0.6, alpha=0.6)
    _setup_axis(ax, Lx, Ly, 'u-velocity')
    cbar = fig.colorbar(cf, ax=ax, fraction=0.046, pad=0.04)
    _setup_colorbar(cbar)
    # constrained_layout=True 确保四图尺寸一致

    if filename:
        fig.savefig(filename, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    return fig


def plot_v_velocity(u, v, p, Re, Lx=1.0, Ly=1.0, levels=15, filename=None, show=False):
    X, Y, _u_center, v_center = _prepare_center_fields(u, v, p, Lx=Lx, Ly=Ly)

    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(1, 1, figsize=(6.5, 5.5), constrained_layout=True)
    cf = ax.contourf(X, Y, v_center, levels, cmap='jet')
    ax.contour(X, Y, v_center, levels=levels, colors='k', linewidths=0.6, alpha=0.6)
    _setup_axis(ax, Lx, Ly, 'v-velocity')
    cbar = fig.colorbar(cf, ax=ax, fraction=0.046, pad=0.04)
    _setup_colorbar(cbar)
    # constrained_layout=True 确保四图尺寸一致

    if filename:
        fig.savefig(filename, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    return fig


def plot_pressure(u, v, p, Re, Lx=1.0, Ly=1.0, levels=15, filename=None, show=False):
    X, Y, _u_center, _v_center = _prepare_center_fields(u, v, p, Lx=Lx, Ly=Ly)

    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(1, 1, figsize=(6.5, 5.5), constrained_layout=True)
    cf = ax.contourf(X, Y, p, levels, cmap='jet')
    ax.contour(X, Y, p, levels=levels, colors='k', linewidths=0.6, alpha=0.6)
    _setup_axis(ax, Lx, Ly, 'Pressure Field')
    cbar = fig.colorbar(cf, ax=ax, fraction=0.046, pad=0.04)
    _setup_colorbar(cbar)
    # constrained_layout=True 确保四图尺寸一致

    if filename:
        fig.savefig(filename, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    return fig


def plot_streamlines(u, v, p, Re, Lx=1.0, Ly=1.0, density=1.5, filename=None, show=False):
    X, Y, u_center, v_center = _prepare_center_fields(u, v, p, Lx=Lx, Ly=Ly)

    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(1, 1, figsize=(6.5, 5.5), constrained_layout=True)
    speed = np.sqrt(u_center ** 2 + v_center ** 2)
    st = ax.streamplot(
        X,
        Y,
        u_center,
        v_center,
        color=speed,
        cmap='jet',
        density=density,
        linewidth=1.0,
        arrowsize=1.2,
    )
    _setup_axis(ax, Lx, Ly, 'Streamlines')
    cbar = fig.colorbar(st.lines, ax=ax, fraction=0.046, pad=0.04)
    _setup_colorbar(cbar)
    # constrained_layout=True 确保四图尺寸一致

    if filename:
        fig.savefig(filename, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    return fig


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
    # 兼容接口：仍返回 2x2 Figure（用于脚本或你仍想一次性保存）
    X, Y, u_center, v_center = _prepare_center_fields(u, v, p, Lx=Lx, Ly=Ly)

    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.unicode_minus'] = False

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle(f'Lid-Driven Cavity Flow Results (Re={Re})', fontsize=24, fontweight='bold', y=0.96)

    levels = 15

    ax1 = axes[0, 0]
    cf1 = ax1.contourf(X, Y, u_center, levels, cmap='jet')
    ax1.contour(X, Y, u_center, levels=levels, colors='k', linewidths=0.6, alpha=0.6)
    _setup_axis(ax1, Lx, Ly, 'u-velocity')
    _setup_colorbar(fig.colorbar(cf1, ax=ax1, fraction=0.046, pad=0.04))

    ax2 = axes[0, 1]
    cf2 = ax2.contourf(X, Y, v_center, levels, cmap='jet')
    ax2.contour(X, Y, v_center, levels=levels, colors='k', linewidths=0.6, alpha=0.6)
    _setup_axis(ax2, Lx, Ly, 'v-velocity')
    _setup_colorbar(fig.colorbar(cf2, ax=ax2, fraction=0.046, pad=0.04))

    ax3 = axes[1, 0]
    cf3 = ax3.contourf(X, Y, p, levels, cmap='jet')
    ax3.contour(X, Y, p, levels=levels, colors='k', linewidths=0.6, alpha=0.6)
    _setup_axis(ax3, Lx, Ly, 'Pressure Field')
    _setup_colorbar(fig.colorbar(cf3, ax=ax3, fraction=0.046, pad=0.04))

    ax4 = axes[1, 1]
    speed = np.sqrt(u_center ** 2 + v_center ** 2)
    st = ax4.streamplot(
        X,
        Y,
        u_center,
        v_center,
        color=speed,
        cmap='jet',
        density=1.5,
        linewidth=1.0,
        arrowsize=1.2,
    )
    _setup_axis(ax4, Lx, Ly, 'Streamlines')
    _setup_colorbar(fig.colorbar(st.lines, ax=ax4, fraction=0.046, pad=0.04))

    fig.tight_layout(rect=(0, 0.03, 1, 0.95))

    if filename:
        fig.savefig(filename, dpi=300, bbox_inches='tight')
    if show:
        plt.show()
    return fig
