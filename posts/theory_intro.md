### 标准DMD 
1. 根据数据定义矩阵$\mathbf{X}$和$\mathbf{Y}$：

   $$
   \mathbf{X} = (x_1, \ldots, x_{m-1}) \quad , \quad \mathbf{Y} = (x_2, \ldots, x_m)
   $$

2. 对矩阵$\mathbf{X}$进行（降维）奇异值分解（SVD），即计算$\mathbf{U}$、$\Sigma$和$\mathbf{V}$，使得

   $$
   \mathbf{X} = \mathbf{U} \Sigma \mathbf{V}^*
   $$

   其中$\mathbf{U} \in \mathbb{C}^{n \times r}$、$\Sigma \in \mathbb{C}^{r \times r}$和$\mathbf{V} \in \mathbb{C}^{(m-1) \times r}$，$r$为$\mathbf{X}$的秩。

3. 设$\tilde{\mathbf{A}}$由以下定义

   $$
   \tilde{\mathbf{A}} = \mathbf{U}^* \mathbf{Y} \mathbf{V} \Sigma^{-1}
   $$

4. 计算$\tilde{\mathbf{A}}$的特征分解，得到一组$r$向量、$\mathbf{w}$和特征值$\lambda$，使得

   $$
   \tilde{\mathbf{A}} \mathbf{w} = \lambda \mathbf{w}
   $$

5. 由以下定义的DMD模式并L2范数归一化：

   $$
   \varphi = \frac{\mathbf{U} \mathbf{w}}{\|\mathbf{U} \mathbf{w}\|_2}
   $$
   



### 精确DMD
1. 根据数据定义矩阵$\mathbf{X}$和$\mathbf{Y}$：

   $$
   \mathbf{X} = (x_1, \ldots, x_{m-1}) \quad , \quad \mathbf{Y} = (x_2, \ldots, x_m)
   $$

2. 对矩阵$\mathbf{X}$进行（降维）奇异值分解（SVD），即计算$\mathbf{U}$、$\Sigma$和$\mathbf{V}$，使得

   $$
   \mathbf{X} = \mathbf{U} \Sigma \mathbf{V}^*
   $$

   其中$\mathbf{U} \in \mathbb{C}^{n \times r}$、$\Sigma \in \mathbb{C}^{r \times r}$和$\mathbf{V} \in \mathbb{C}^{(m-1) \times r}$，$r$为$\mathbf{X}$的秩。

3. 设$\tilde{\mathbf{A}}$由以下定义

   $$
   \tilde{\mathbf{A}} = \mathbf{U}^* \mathbf{Y} \mathbf{V} \Sigma^{-1}
   $$

4. 计算$\tilde{\mathbf{A}}$的特征分解，得到一组$r$向量、$\mathbf{w}$和特征值$\lambda$，使得

   $$
   \tilde{\mathbf{A}} \mathbf{w} = \lambda \mathbf{w}
   $$

5. 对于每一对$(w, \lambda)$，我们都有一个DMD特征值，即$\lambda$本身，以及一个由以下定义的DMD模式

   $$
   \varphi = \frac{1}{\lambda} \mathbf{Y} \mathbf{V} \Sigma^{-1} \mathbf{w}
   $$
   
## SPDMD


1. 通过解决下面的优化问题，寻找一个稀疏结构，在提取模态数量与近似误差之间实现用户定义的权衡：

   $$
   \underset{\alpha}{\text{minimize}} \quad J(\alpha) + \gamma \sum_{i=1}^{r} |\alpha_i|.
   $$

   其中：

   $$
   J(\alpha) = \|\Sigma V^* - \mathbf{w} D_{\alpha} V_{\text{and}}\|_F^2
   $$

   $$
   = \|\Sigma V^* - \mathbf{w}
   \begin{pmatrix}
   \alpha_1 & 0 & \cdots & 0 \\
   0 & \alpha_2 & \cdots & 0 \\
   \vdots & \vdots & \ddots & \vdots \\
   0 & 0 & \cdots & \alpha_i
   \end{pmatrix}
   \begin{pmatrix}
   1 & \lambda_1 & \cdots & \lambda_1^{N-2} \\
   1 & \lambda_2 & \cdots & \lambda_2^{N-2} \\
   \vdots & \vdots & \ddots & \vdots \\
   1 & \lambda_m & \cdots & \lambda_i^{N-2}
   \end{pmatrix}
   \|_F^2
   $$

   \(\gamma\) 是惩罚参数，\(\alpha\) 是未知的振幅矩阵，\(\sum_{i=1}^{r} |\alpha_i|\) 表示 DMD 振幅绝对值之和。

2. 在实验或数值快照的近似质量与 DMD 模态数量之间达到理想的平衡后，我们固定未知振幅向量的稀疏结构，并通过求解以下约束凸优化问题，仅确定非零振幅，即抛光振幅：

   $$
   \begin{align*}
   \underset{\alpha}{\text{minimize}} \quad & J(\alpha) \\
   \text{subject to} \quad & E^T \alpha = 0.
   \end{align*}
   $$

### 优化DMD
1. 给定快照矩阵 \(\mathbf{X}\) 和 \(\lambda\) 的初始猜测。
   1. 设 $\mathbf{X}_1 = (x_1, \ldots, x_{m-1}), \mathbf{X}_2 = (x_2, \ldots, x_m),T = \text{diag}(t_1 - t_0, t_2 - t_1, \ldots, t_m - t_{m-1})$,根据数据定义矩阵 \(Y\) 和 \(Z\)：

   $$
   Y = \frac{\mathbf{X}_1 + \mathbf{X}_2}{2}, \quad Z = (\mathbf{X}_2 - \mathbf{X}_1) T^{-1}.
   $$

   2. 对矩阵 \(Y\) 进行（降维）奇异值分解（SVD），即计算 \(\mathbf{U}\)、\(\Sigma\) 和 \(\mathbf{V}\)，使得

   $$
   Y = \mathbf{U} \Sigma \mathbf{V}^*,
   $$

   其中 \(\mathbf{U} \in \mathbb{C}^{n \times r}\)、\(\Sigma \in \mathbb{C}^{r \times r}\) 和 \(\mathbf{V} \in \mathbb{C}^{m \times r}\)，\(r\) 为 \(Y\) 的秩。

   3. 设 \(\tilde{\mathbf{A}}\) 由以下定义

   $$
   \tilde{\mathbf{A}} = \mathbf{U}^* Z \mathbf{V} \Sigma^{-1}.
   $$

   4. 计算 \(\tilde{\mathbf{A}}\) 的特征分解，得到一组 \(r\) 向量、\(\mathbf{w}\) 和特征值 \(\lambda\)，使得

   $$
   \tilde{\mathbf{A}} \mathbf{w} = \lambda \mathbf{w}.
   $$

   5. 返回快照矩阵$\mathbf{X}_1 = (x_1, \ldots, x_{m})$和特征值$\lambda$。

2. 计算 \(\mathbf{X}\) 的秩 \(r\) 截断 SVD，即计算 \(\mathbf{U}_r \in \mathbb{C}^{n \times r}\)，\(\Sigma_r \in \mathbb{C}^{r \times r}\) 和 \(\mathbf{V}_r \in \mathbb{C}^{ m \times r}\)，使得

   $$
   \mathbf{X}_r = \mathbf{U}_r \Sigma_r \mathbf{V}_r^*.
   $$

3. 计算求解 \(\hat{\lambda}\) 和 \(\hat{\mathbf{B}}\)

   $$
   \text{minimize} \|\mathbf{V}_r \Sigma_r - \Phi(\lambda) \mathbf{B}\|_F \quad \text{over } \lambda \in \mathbb{C}^r, \mathbf{B} \in \mathbb{C}^{r \times r},
   $$

   使用变量投影算法逼近线性算子A以降低噪声影响.其中，特征值$\lambda$作为迭代参数，决定了特征函数$\Phi$和振幅相关矩阵$\mathbf{B}$的取值。

4. 设置 \(\lambda_i = \hat{\lambda}_i\) 和计算归一化模态：

   $$
   \varphi_i = \frac{1}{\|\mathbf{U}_r \hat{\mathbf{B}}^T(:,i)\|_2} \mathbf{U}_r \hat{\mathbf{B}}^T(:,i),
   $$

   保存振幅 \(b_i = \|\mathbf{U}_r \hat{\mathbf{B}}^T(:,i)\|_2\)。

### 高阶DMD
1. 两次截断(HOSVD截断、建立高阶矩阵、SVD截断)
   1. 第一次HOSVD截断奇异值：

   $$
   \hat{V}_{i_1i_2i_3k}^R = \sum_{p_1=1}^{P_1} \sum_{p_2=1}^{P_2} \sum_{p_3=1}^{P_3} \sum_{n=1}^{N} S_{p_1p_2p_3n} U_{i_1p_1} W_{i_2p_2}^{(y)} W_{i_3p_3}^{(x)} T_{kn}
   $$
   时间矩阵 \( T \) 进行奇异值截断后的矩阵，称为 \(\hat{V}_1^K\)。

   2. 利用高阶Koopman假设建立高阶矩阵:
   $$
   \hat{V}_{d+1}^K \simeq \hat{A}_1 \hat{V}_1^{K-d} + \hat{A}_2 \hat{V}_2^{K-d+1} + \ldots + \hat{A}_d \hat{V}_d^{K-1}
   $$

   $$
   \begin{align*}
   \begin{bmatrix}
   \hat{V}_2^{K-d+1} \\
   \vdots \\
   \hat{V}_d^{K-1} \\
   \hat{V}_{d+1}^K
   \end{bmatrix}
   &=
   \begin{bmatrix}
   0 & I & 0 & \cdots & 0 & 0 \\
   0 & 0 & I & \cdots & 0 & 0 \\
   \vdots & \vdots & \vdots & \ddots & \vdots & \vdots \\
   0 & 0 & 0 & \cdots & I & 0 \\
   \hat{A}_1 & \hat{A}_2 & \hat{A}_3 & \cdots & \hat{A}_{d-1} & \hat{A}_d
   \end{bmatrix}
   \begin{bmatrix}
   \hat{V}_1^{K-d} \\
   \hat{V}_2^{K-d+1} \\
   \vdots \\
   \hat{V}_d^{K-1}
   \end{bmatrix}
   \end{align*}
   $$

   3. 第二次SVD截断奇异值:
   $$
   (\hat{V}^*)_1^{K-d+1} = U^* \Sigma^* (T^*)^T = U^* (\hat{V}_1^{K-d+1})^*
   $$

2. 对$\hat{V}_1^{K-d}$进行标准动态模式分解，包括总体最小二乘法拟合并归一化处理得到振幅和模态$a_m、u_m$。
   
3. 能量排序准则(模态截断准则)
$$
I_m = \sum_{k=1}^{K} \left| a_m e^{(\delta_n + i \omega_n)(k-1) \Delta t} \right| \left\| u_m \right\|_F^2 \times \Delta t \quad \text{for } k = 1, \ldots, K
$$

$$
\frac{I_{M+1}}{I_1} \leq \varepsilon_{DMD}
$$

