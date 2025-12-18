# `methods.py` 计算方法与计算步骤（详细说明）

> 本说明对应当前工程根目录中的 `methods.py`，核心函数为：
>
> - `lid_driven_cavity_mac(...)`
>
> 它使用 **MAC（Marker-And-Cell）交错网格** + **有限差分**，通过 **投影法（Projection / Chorin 法）** 求解二维不可压缩 Navier–Stokes 方程的典型算例：**顶盖驱动方腔流（Lid-Driven Cavity）**。
>
> 本文尽量把代码里的每一步“它在算什么、为什么这么算、数组形状如何对应物理位置、边界条件怎么施加、压力泊松方程怎么迭代”等都讲清楚，便于你以后改模型、改格式或做性能优化。

---

## 1. 求解的物理方程与无量纲形式

二维不可压缩 Navier–Stokes 方程（无量纲）可写为：

- 连续方程（不可压缩约束）

\[
\nabla \cdot \mathbf{u} = 0
\]

- 动量方程

\[
\frac{\partial \mathbf{u}}{\partial t} + \nabla \cdot (\mathbf{u}\mathbf{u}) = -\nabla p + \frac{1}{Re}\nabla^2 \mathbf{u}
\]

其中：

- \(\mathbf{u}=(u,v)\) 为速度
- \(p\) 为压力（严格说是“归一化压力/动压”）
- \(Re\) 为雷诺数

### 为什么需要“压力泊松方程”？
不可压缩条件 \(\nabla\cdot\mathbf{u}=0\) 会把压力变成一个“约束变量”：压力本身不由独立的时间演化方程给出，而是用来修正速度，使速度场满足散度为 0。

因此常见做法是 **投影法**：

1) 先不考虑压力（或用旧压力）求出一个“中间速度” \(\mathbf{u}^*\)

2) 通过求解压力泊松方程得到压力 \(p\)

3) 用压力梯度修正 \(\mathbf{u}^*\) 得到满足不可压缩的 \(\mathbf{u}^{n+1}\)

---

## 2. 网格与变量存储：MAC 交错网格

代码中采用 MAC 交错网格（Staggered Grid）：

- 压力 \(p\) 存在 **单元中心（cell center）**
- 速度 \(u\) 存在 **垂直面（vertical faces）**
- 速度 \(v\) 存在 **水平面（horizontal faces）**

这可以避免压力-速度的奇偶解（checkerboard pressure）问题，也让散度/梯度离散更自然。

### 数组形状对应关系
设网格单元数为 `nx` × `ny`，区域为 \([0,Lx]\times[0,Ly]\)，则：

- `p.shape == (ny, nx)`
  - 每个单元中心一个压力

- `u.shape == (ny, nx+1)`
  - x 方向速度在垂直面上：每行 `nx+1` 个面

- `v.shape == (ny+1, nx)`
  - y 方向速度在水平面上：每列 `ny+1` 个面

直观理解：

- 一个 `nx×ny` 的单元网格有 `nx+1` 条竖线面、`ny+1` 条横线面。

---

## 3. 顶盖驱动方腔流的边界条件

在这个算例中，方腔四周为固壁：

- 左壁、右壁、下壁：无滑移 `u=v=0`
- 上壁（顶盖）：
  - `u = 1.0`（代码中 `u_top = 1.0`）
  - `v = 0`

压力边界条件一般给 **Neumann**：\(\partial p/\partial n = 0\)（壁面法向压力梯度为 0），并用“减去均值”消除压力的常数不唯一性。

---

## 4. 主函数 `lid_driven_cavity_mac()` 的整体流程（大纲）

这个函数基本按以下时间步循环结构执行：

1. 初始化网格、数组与系数
2. 对每个时间步 `n = 0..max_iter-1`：
   1) **预测步（动量方程）**：由 \(u^n, v^n\) 得到中间速度 \(u^*, v^*\)
   2) **压力泊松方程（PPE）**：由 \(\nabla\cdot\mathbf{u}^*\) 构造源项，迭代求解压力 \(p\)
   3) **修正步（Projection）**：用压力梯度修正速度，得到 \(u^{n+1}, v^{n+1}\)
   4) 施加边界条件、检查收敛、按需保存快照
3. 循环结束后确保保存最后一帧并返回

接下来按代码顺序展开讲。

---

## 5. 初始化阶段（代码第 1 部分）

### 5.1 计算网格步长

```python
Lx, Ly = 1.0, 1.0
dx = Lx / nx
dy = Ly / ny
```

- `nx, ny` 表示单元（cell）数量
- `dx, dy` 为单元宽高

### 5.2 初始化变量数组

```python
u = np.zeros((ny, nx + 1))
v = np.zeros((ny + 1, nx))
p = np.zeros((ny, nx))
```

这对应 MAC 网格的存储方式（见第 2 节）。

### 5.3 保存策略 `save_interval`

- `save_interval=None`：**不存全历史**，只在结束时保存最后一帧（最省内存）
- `save_interval=N`：每 `N` 步保存一次快照（并且也会保存最后一帧）

函数返回仍是 `u_list, v_list, p_list`，但在 `save_interval=None` 的情况下，list 中通常只有 1 帧（最后一帧）。

### 5.4 预计算常用系数

```python
inv_Re = 1.0 / Re
dx2 = dx ** 2
dy2 = dy ** 2
denom = 2 * (dx2 + dy2)
inv_denom = 1.0 / denom
```

这些用于扩散项和压力泊松方程离散，避免在循环中重复计算。

### 5.5 稳定性提示（CFL 与扩散限制）

代码打印：

- CFL 约束：`dt <= min(dx,dy)/u_max_est`
- 扩散约束（显式扩散稳定性）：`dt <= 0.25*Re*min(dx,dy)^2`

这并不强制截断 `dt`，只是提醒用户：`dt` 太大可能会不稳定。

---

## 6. 压力求解方法：Jacobi / Gauss-Seidel / SOR

在 PPE（Pressure Poisson Equation）部分，代码可选：

- `jacobi`
- `gauss_seidel`
- `sor`

其中：

- Gauss-Seidel 相当于 SOR 的 `omega=1`
- SOR（超松弛）通常收敛更快，`omega` 常取 1.7~1.9

### 6.1 红黑（Red-Black）更新掩码

为了向量化 Gauss-Seidel / SOR，代码使用棋盘格更新：

- 红点：`(i+j)%2==0`
- 黑点：`(i+j)%2==1`

这样可以在 numpy 中批量更新红点、再批量更新黑点，达到类似 GS 的“分块顺序更新”效果。

---

## 7. 时间步循环（核心）

```python
for n in tqdm(range(max_iter), ...):
    un = u.copy()
    vn = v.copy()
    ...
```

这里 `un, vn` 是上一时间步的拷贝，用于：

- 构造显式对流/扩散项
- 用于收敛性比较（u 与 un 的差）

下面按 A/B/C/D 四块解释。

---

## 8. A. 预测步：求解动量方程得到中间速度 `u_star`, `v_star`

预测步的目标：暂时不强制散度为 0，先解：

\[
\frac{\mathbf{u}^* - \mathbf{u}^n}{\Delta t} = -\nabla\cdot(\mathbf{u}\mathbf{u}) + \frac{1}{Re}\nabla^2\mathbf{u}
\]

注意：代码把压力项放到后面修正步中处理。

### 8.1 U 动量方程（更新 u 的内部面）

#### 8.1.1 Ghost Cell 扩展：`un_pad`

```python
un_pad = np.pad(un, ((1, 1), (0, 0)), 'edge')
un_pad[0, :] = -un[0, :]
un_pad[-1, :] = 2 * u_top - un[-1, :]
```

这里的 `np.pad(..., 'edge')` 先用边界值外推。
随后用两行显式覆盖实现固壁/顶盖边界：

- 底壁无滑移：通常等价于壁面外侧虚点速度取负（镜像法）实现壁面速度 0
- 顶盖：壁面速度为 `u_top`，对 ghost 值做 `2*u_top - inside`，使得壁面插值速度为 `u_top`

> 注意：此处只在 y 方向 pad，因为 u 的扩散项需要用到 y 方向邻点；x 方向的边界更多通过直接强制 `u_star[:,0]=0` 等处理。

#### 8.1.2 取内部 u

```python
u_c = un[:, 1:-1]
```

`u_c` 对应内部垂直面，去掉左右边界两列（边界列最终会被强制成 0）。

#### 8.1.3 扩散项 `diff_u`

```python
diff_u = (1/Re) * [d2u/dx2 + d2u/dy2]
```

离散使用中心差分：

- x 方向二阶：`(u[i+1]-2u[i]+u[i-1])/dx^2`
- y 方向二阶：`(u[j+1]-2u[j]+u[j-1])/dy^2`

#### 8.1.4 对流项：`du2_dx` 与 `duv_dy`

不可压缩流动常用保守形式：

- \(\partial (u^2)/\partial x\)
- \(\partial (uv)/\partial y\)

代码中：

```python
du2_dx = (((u_c + un[:, 2:]) / 2) ** 2 - ((u_c + un[:, :-2]) / 2) ** 2) / dx
```

这里 `(u_c + un[:, 2:]) / 2` 是把 `u` 插值到面之间的“半格点”，再平方，体现了保守格式的通量差分。

`duv_dy` 更复杂，因为需要 v 在 u 的位置进行插值：

- `v` 位于水平面，上下两个 v 面围出 u 所在的角点
- 代码取 `v_nw, v_ne, v_sw, v_se` 四个点做平均

然后对 `u` 在 y 方向也做平均，使得 `u*v` 在同一位置定义。

#### 8.1.5 显式时间推进得到 `u_star`

```python
u_star[:, 1:-1] = u_c + dt * (-du2_dx - duv_dy + diff_u)
```

即：

\[
 u^* = u^n + \Delta t\,\left(-\frac{\partial u^2}{\partial x}-\frac{\partial (uv)}{\partial y}+\frac{1}{Re}\nabla^2 u\right)
\]

随后强制边界：

```python
u_star[:, 0] = 0
u_star[:, -1] = 0
```

### 8.2 V 动量方程（更新 v 的内部面）

v 的更新同理，只是 x/y 角色交换。

#### 8.2.1 Ghost Cell 扩展：`vn_pad`

```python
vn_pad = np.pad(vn, ((0, 0), (1, 1)), 'edge')
vn_pad[:, 0] = -vn[:, 0]
vn_pad[:, -1] = -vn[:, -1]
```

这里在 x 方向 pad，并令左右壁满足无滑移（镜像法）。

#### 8.2.2 扩散项 `diff_v`

同样是中心差分计算 \(\nabla^2 v\)。

#### 8.2.3 对流项：`dv2_dy` 与 `duv_dx`

- `dv2_dy` 类似 `du2_dx`
- `duv_dx` 需要把 u 插值到 v 的位置（四点平均）

#### 8.2.4 得到 `v_star` 并强制边界

```python
v_star[1:-1, :] = v_c + dt * (-duv_dx - dv2_dy + diff_v)

v_star[0, :] = 0
v_star[-1, :] = 0
```

---

## 9. B. 压力泊松方程（PPE）：由 `u_star`, `v_star` 得到压力 `p`

预测步后，\(\mathbf{u}^*\) 一般不满足 \(\nabla\cdot\mathbf{u}=0\)。
为了在下一步修正速度，需要求解压力使：

\[
\mathbf{u}^{n+1} = \mathbf{u}^* - \Delta t \nabla p
\]

对两边取散度，并要求 \(\nabla\cdot\mathbf{u}^{n+1}=0\)：

\[
\nabla^2 p = \frac{1}{\Delta t}\nabla\cdot\mathbf{u}^*
\]

这就是压力泊松方程。

### 9.1 计算散度与源项 b

代码：

```python
div_u_star = (u_star[:, 1:] - u_star[:, :-1]) / dx + (v_star[1:, :] - v_star[:-1, :]) / dy
b = div_u_star / dt
```

这里的散度正好在 **单元中心**，与 `p.shape == (ny,nx)` 对齐。

### 9.2 压力边界：Neumann（dp/dn = 0）

实现方式是对 `p` 做一圈 pad，然后把 ghost 单元用邻近内点复制：

```python
p_pad = np.pad(p, ((1, 1), (1, 1)), 'edge')

p_pad[0, 1:-1] = p_pad[1, 1:-1]      # bottom
p_pad[-1, 1:-1] = p_pad[-2, 1:-1]    # top
p_pad[1:-1, 0] = p_pad[1:-1, 1]      # left
p_pad[1:-1, -1] = p_pad[1:-1, -2]    # right
```

这等价于法向一阶导数为 0。

### 9.3 离散形式与更新公式

内部点的离散：

\[
\frac{p_{i+1,j}-2p_{i,j}+p_{i-1,j}}{dx^2} + \frac{p_{i,j+1}-2p_{i,j}+p_{i,j-1}}{dy^2} = b_{i,j}
\]

整理得：

\[
 p_{i,j} = \frac{dy^2(p_{i+1,j}+p_{i-1,j}) + dx^2(p_{i,j+1}+p_{i,j-1}) - dx^2dy^2 b_{i,j}}{2(dx^2+dy^2)}
\]

代码中的 `inv_denom` 就是 \(1/(2(dx^2+dy^2))\)。

### 9.4 三种迭代器

#### 9.4.1 Jacobi

- 用旧值计算新值
- 每次迭代更新整张网格
- 收敛较慢，但实现简单

代码中：

```python
p_old_inner = p_pad[1:-1, 1:-1].copy()
p_new = (...)*inv_denom
p_pad[1:-1,1:-1] = p_new
```

#### 9.4.2 Gauss-Seidel（omega=1）与 SOR

- GS：用“最新的已更新值”参与下一点更新，收敛更快
- SOR：在 GS 基础上增加超松弛：

\[
 p^{new} = (1-\omega)p^{old} + \omega p^{GS}
\]

代码通过红黑更新实现向量化：

1) 先计算一次 `p_gs`
2) 更新红点 `mask_red`
3) 再计算一次 `p_gs`
4) 更新黑点 `mask_black`

并用 `current_omega` 控制松弛因子。

### 9.5 PPE 收敛判定

每 10 次迭代计算一次最大差：

```python
diff = max(abs(p_new - p_old_inner))
if diff < Ptol: break
```

> 注意：这是一种常见但并不唯一的判据；也可以用残差（离散方程左右差）作为更严格的判据。

### 9.6 压力归一化（去均值）

泊松方程在 Neumann 边界下压力只确定到一个常数，因此代码：

```python
p -= np.mean(p)
```

这不会改变压力梯度（因此不会改变速度修正），但能避免压力整体漂移导致数值不稳定。

---

## 10. C. 修正步（Projection）：用压力梯度修正速度

修正公式：

\[
\mathbf{u}^{n+1} = \mathbf{u}^* - \Delta t\nabla p
\]

在 MAC 网格上：

- `u` 位于垂直面，因此用相邻两个 cell center 的压力差来近似 \(\partial p/\partial x\)
- `v` 位于水平面，因此用相邻两个 cell center 的压力差来近似 \(\partial p/\partial y\)

代码：

```python
u[:, 1:-1] = u_star[:, 1:-1] - dt * (p[:, 1:] - p[:, :-1]) / dx
v[1:-1, :] = v_star[1:-1, :] - dt * (p[1:, :] - p[:-1, :]) / dy
```

修正后再次强制边界：

```python
u[:, 0] = 0
u[:, -1] = 0
v[0, :] = 0
v[-1, :] = 0
u[-1, :] = u_top
```

其中 `u[-1,:]=u_top` 是顶盖速度条件。

---

## 11. D. 收敛检查与保存策略

### 11.1 收敛检查

每 100 步计算一次速度变化的相对范数：

```python
err_u = ||u - un|| / (||un|| + 1e-12)
err_v = ||v - vn|| / (||vn|| + 1e-12)
```

若 `err_u < Vtol` 且 `err_v < Vtol`，认为收敛并跳出循环。

> 这相当于在判断“稳态”是否达到（速度不再变化）。

### 11.2 保存快照（解决内存占用问题）

- 若 `save_interval is not None`：每 `n % save_interval == 0` 保存一次
- 无论如何，循环结束后都会保存最后一帧

这保证：

- 不保存历史时，list 里至少有 1 帧
- 保存历史时，list 里有若干帧 + 最后一帧

---

## 12. 结果返回与后处理衔接

函数返回：

```python
return u_list, v_list, p_list
```

在 `FDM_main.py` 中通常取最后一帧：

```python
u_final = u_list[-1]
v_final = v_list[-1]
p_final = p_list[-1]
```

然后用于：

- 中心线剖面对比（Ghia 基准）
- 速度/压力云图 + 流线图

---

## 13. 一些常见疑问/注意点（对照代码理解）

### 13.1 为什么对流项写成“通量差分”而不是 `u*du/dx`？

保守形式 \(\partial(u^2)/\partial x\) 在数值上更稳定，且与有限体积思想一致，尤其在不可压缩流中常用。

### 13.2 为什么要用 pad / ghost cell？

因为中心差分需要访问边界外侧的点。Ghost cell 是用来把边界条件“编码进差分模板”里，使得内点更新公式不需要写很多 if/else。

### 13.3 为什么压力泊松方程要迭代很多次？

泊松方程是一个全局耦合方程，直接求解需要稀疏矩阵求解器；这里用 Jacobi/GS/SOR 属于经典的迭代解法，收敛速度取决于网格大小与 `omega`。

### 13.4 为什么要 `p -= mean(p)`？

Neumann 边界下压力只差一个常数，减去均值是固定这个常数，使压力不会整体漂移。

### 13.5 `max_ppe_iter=2000` 为什么要设置？

防止某些参数导致 PPE 不收敛而无限循环。

---

## 14. 如果你后续想进一步提升稳定性/速度（可选建议）

> 你目前不要求改代码，这里只是给你后续优化的方向。

1. **减少 `np.pad` 与 `.copy()` 的临时数组**（可用预分配 ghost 数组、或用切片就地更新）
2. PPE 改用 `scipy.sparse` + 共轭梯度/多重网格（速度会快很多）
3. 显式对流+扩散在高 Re 时更容易不稳定，可考虑：
   - 更小 dt
   - 二阶/TV D 限幅格式
   - 半隐式扩散
4. `u[-1,:]=u_top` 的实现方式可以更严格地只赋顶壁面对应的 u 面（取决于你如何定义 u 的 y 位置）

---

## 15. 结语：一句话总结本程序在做什么

- 用 **MAC 交错网格**对不可压缩 N-S 方程离散
- 每步先用显式格式求中间速度 \(u^*,v^*\)
- 再解 **压力泊松方程**，用压力梯度投影修正速度，使散度为 0
- 迭代到稳态或最大步数，输出最后/间隔快照

如果你希望我再补一份“配图版说明”（把 u/v/p 在交错网格的位置画出来，对照数组下标和差分模板），我也可以继续在 `备注.md` 里补充一节。
