import matplotlib.pyplot as plt
import numpy as np

def plot_velocity_magnitude(u, v, grid_size, Re):
    """绘制速度大小云图"""
    velocity_magnitude = np.sqrt(u**2 + v**2)
    x = np.linspace(0, 1, grid_size)
    y = np.linspace(0, 1, grid_size)
    X, Y = np.meshgrid(x, y)

    fig, ax = plt.subplots(figsize=(8, 6))
    c = ax.contourf(X, Y, velocity_magnitude, levels=20, cmap='jet')
    plt.colorbar(c, ax=ax, label='Velocity Magnitude')
    ax.set_title(f"Velocity Magnitude (Re={Re})")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return fig

def plot_streamlines(u, v, grid_size, Re):
    """绘制流线图"""
    velocity_magnitude = np.sqrt(u**2 + v**2)
    x = np.linspace(0, 1, grid_size)
    y = np.linspace(0, 1, grid_size)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    strm = ax.streamplot(x, y, u, v, color=velocity_magnitude, cmap='autumn', density=1.5)
    plt.colorbar(strm.lines, ax=ax, label='Speed')
    ax.set_title(f"Streamlines (Re={Re})")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return fig

def plot_pressure(p, grid_size, Re):
    """绘制压力场"""
    x = np.linspace(0, 1, grid_size)
    y = np.linspace(0, 1, grid_size)
    X, Y = np.meshgrid(x, y)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    c = ax.contourf(X, Y, p, levels=20, cmap='viridis')
    plt.colorbar(c, ax=ax, label='Pressure')
    ax.set_title(f"Pressure Field (Re={Re})")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return fig
