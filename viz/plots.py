import matplotlib.pyplot as plt
import numpy as np

# 设置全局绘图风格
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#f1f5f9',
    'axes.labelcolor': '#64748b',
    'xtick.color': '#64748b',
    'ytick.color': '#64748b',
    'text.color': '#334155',
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'figure.dpi': 150
})

def _clean_axis(ax):
    """辅助函数：清理坐标轴样式"""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    # 保持刻度但移除线条
    ax.tick_params(axis='both', which='both', length=0)

def plot_velocity_magnitude(u, v, grid_size, Re):
    """绘制速度大小云图 (Modern Style)"""
    velocity_magnitude = np.sqrt(u**2 + v**2)
    x = np.linspace(0, 1, grid_size)
    y = np.linspace(0, 1, grid_size)
    X, Y = np.meshgrid(x, y)

    fig, ax = plt.subplots(figsize=(6, 5))
    # 使用 'inferno' 或 'magma' 配色，比 'jet' 更现代且对色盲友好
    c = ax.contourf(X, Y, velocity_magnitude, levels=50, cmap='inferno', alpha=0.9)
    
    # 极简 Colorbar
    cbar = plt.colorbar(c, ax=ax, fraction=0.046, pad=0.04)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(size=0)
    
    _clean_axis(ax)
    ax.set_title(f"Velocity Magnitude ($Re={int(Re)}$)", pad=10, fontsize=10, fontweight='bold')
    return fig

def plot_streamlines(u, v, grid_size, Re):
    """绘制流线图 (Modern Style)"""
    velocity_magnitude = np.sqrt(u**2 + v**2)
    x = np.linspace(0, 1, grid_size)
    y = np.linspace(0, 1, grid_size)
    
    fig, ax = plt.subplots(figsize=(6, 5))
    # 流线使用黑色或深灰色，背景可以叠加极淡的速度云图
    ax.contourf(x, y, velocity_magnitude, levels=20, cmap='Greys', alpha=0.15)
    strm = ax.streamplot(x, y, u, v, color='#0f172a', linewidth=0.8, density=1.2, arrowsize=0.8)
    
    _clean_axis(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(f"Streamlines Topology", pad=10, fontsize=10, fontweight='bold')
    return fig

def plot_pressure(p, grid_size, Re):
    """绘制压力场 (Modern Style)"""
    x = np.linspace(0, 1, grid_size)
    y = np.linspace(0, 1, grid_size)
    X, Y = np.meshgrid(x, y)
    
    fig, ax = plt.subplots(figsize=(6, 5))
    # 压力通常有正负，使用发散色系 'RdBu_r' (Red-Blue reversed)
    # 减去均值，使颜色平衡
    p_norm = p - np.mean(p)
    limit = np.max(np.abs(p_norm))
    
    c = ax.contourf(X, Y, p_norm, levels=40, cmap='RdBu_r', vmin=-limit, vmax=limit, alpha=0.9)
    
    cbar = plt.colorbar(c, ax=ax, fraction=0.046, pad=0.04)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(size=0)
    
    _clean_axis(ax)
    ax.set_title(f"Pressure Field (Relative)", pad=10, fontsize=10, fontweight='bold')
    return fig