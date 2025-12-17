import matplotlib.pyplot as plt
import numpy as np

# 设置全局绘图风格：极简白底
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'font.family': 'sans-serif',
    'font.size': 9,
    'axes.grid': False,
    'lines.linewidth': 1.0
})

def _clean_axis(ax):
    """移除坐标轴边框，只保留底部和左侧刻度"""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_color('#dee2e6')
    ax.spines['bottom'].set_color('#dee2e6')
    ax.tick_params(colors='#868e96')

def plot_velocity_magnitude(u, v, grid_size, Re):
    velocity_magnitude = np.sqrt(u**2 + v**2)
    # 不包括边界点以避免边界值影响色阶
    vmin, vmax = 0, np.max(velocity_magnitude[1:-1, 1:-1])
    
    x = np.linspace(0, 1, grid_size)
    y = np.linspace(0, 1, grid_size)
    X, Y = np.meshgrid(x, y)

    fig, ax = plt.subplots(figsize=(6, 5), dpi=150)
    # 使用 'magma' 色系，深色背景显现出速度感
    c = ax.contourf(X, Y, velocity_magnitude, levels=60, cmap='magma', vmin=vmin, vmax=vmax)
    
    cbar = plt.colorbar(c, ax=ax, fraction=0.046, pad=0.04)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(color='#dee2e6', labelcolor='#868e96', size=0)
    
    _clean_axis(ax)
    ax.set_aspect('equal')
    return fig

def plot_streamlines(u, v, grid_size, Re):
    x = np.linspace(0, 1, grid_size)
    y = np.linspace(0, 1, grid_size)
    
    fig, ax = plt.subplots(figsize=(6, 5), dpi=150)
    
    # 背景加一点淡淡的速度场
    velocity = np.sqrt(u**2 + v**2)
    ax.contourf(x, y, velocity, levels=20, cmap='Greys', alpha=0.1)
    
    # 流线使用纯色，突出拓扑结构
    strm = ax.streamplot(x, y, u, v, color='#228be6', linewidth=0.8, density=1.5, arrowsize=0.8)
    
    _clean_axis(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    return fig

def plot_pressure(p, grid_size, Re):
    x = np.linspace(0, 1, grid_size)
    y = np.linspace(0, 1, grid_size)
    X, Y = np.meshgrid(x, y)
    
    fig, ax = plt.subplots(figsize=(6, 5), dpi=150)
    
    # 压力使用发散色系 RdBu_r
    p_norm = p - np.mean(p)
    limit = max(abs(np.min(p_norm)), abs(np.max(p_norm)))
    
    c = ax.contourf(X, Y, p_norm, levels=40, cmap='RdBu_r', vmin=-limit, vmax=limit)
    
    cbar = plt.colorbar(c, ax=ax, fraction=0.046, pad=0.04)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(color='#dee2e6', labelcolor='#868e96', size=0)
    
    _clean_axis(ax)
    ax.set_aspect('equal')
    return fig