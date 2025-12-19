<style>
/* 仅作用于本页：避免影响其他文章/页面 */
.about-page { max-width: 980px; margin: 0 auto; }
.about-lead { color: #495057; font-size: 1.02rem; line-height: 1.75; margin-top: 0.25rem; }
.about-meta { margin: 0.75rem 0 1.1rem; color: #868e96; font-size: 0.92rem; }

.about-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; margin: 0.8rem 0 1.2rem; }
.about-card {
	border: 1px solid #dee2e6;
	border-radius: 12px;
	background: #ffffff;
	padding: 12px 14px;
}
.about-card h3 { margin: 0 0 0.45rem; font-size: 1.02rem; color: #212529; }
.about-card p { margin: 0; color: #495057; line-height: 1.7; }

.about-chip {
	display: inline-block;
	padding: 0.18rem 0.55rem;
	border-radius: 999px;
	border: 1px solid #dee2e6;
	background: #f1f3f5;
	color: #495057;
	font-size: 0.86rem;
	font-weight: 600;
	margin-right: 0.35rem;
	margin-bottom: 0.35rem;
}

.about-callout {
	border-left: 4px solid #d0ebff;
	background: #f8f9fa;
	padding: 10px 12px;
	border-radius: 10px;
	color: #495057;
	line-height: 1.7;
}

.about-section-title { margin-top: 1.2rem; }
.about-kv { color: #495057; }
.about-kv strong { color: #212529; }

.about-divider { height: 1px; background: #e9ecef; border: 0; margin: 1.1rem 0; }
</style>

<div class="about-page">

# 项目介绍

<p class="about-lead">
本项目为 <strong>二维顶盖驱动方腔流（Lid-Driven Cavity Flow）</strong> 的数值求解与可视化展示，使用 Streamlit 构建交互式网页，便于进行参数试验、结果对比与算法学习。
</p>

<div class="about-meta">
运行方式：Streamlit / Python　｜　典型用途：数值方法验证、基准对比（Ghia 1982）、教学演示
</div>

<div>
	<span class="about-chip">二维不可压 N-S</span>
	<span class="about-chip">MAC 交错网格</span>
	<span class="about-chip">有限差分</span>
	<span class="about-chip">压力泊松方程</span>
	<span class="about-chip">Jacobi / GS / SOR</span>
</div>

<hr class="about-divider" />

## 二维顶盖驱动方腔流（为什么它经典？）

<div class="about-callout">
由于其边界条件与几何形状简单，但仍包含明显的非线性与涡结构演化，顶盖驱动方腔流长期以来被用作：
<br/>（1）流体力学与 CFD 入门的标准算例；（2）验证数值离散与压力耦合算法正确性的基准问题；（3）与深度学习方法（如 PINN）进行可比对的基准场。
</div>

## 网站模块

<div class="about-grid">
	<div class="about-card">
		<h3>1) 项目介绍</h3>
		<p>说明项目目标、数值模型与页面使用方法，帮助快速上手。</p>
	</div>
	<div class="about-card">
		<h3>2) CFD 计算模拟</h3>
		<p>配置 Re、网格与求解器参数，运行求解并查看速度/压力/流线及中心线对比结果。</p>
	</div>
	<div class="about-card">
		<h3>3) 知识库 / 文章</h3>
		<p>记录核心算法、离散推导与结果对比，作为学习与复现的笔记入口。</p>
	</div>
</div>

## 数值方法概览（简要）

<div class="about-kv">
<strong>离散框架：</strong>MAC 交错网格 + 有限差分（对流/扩散项离散）<br/>
<strong>压力耦合：</strong>投影法（预测-校正）/ 压力泊松方程（PPE）<br/>
<strong>PPE 求解：</strong>Jacobi、Gauss-Seidel、SOR（含松弛因子 $\omega$）
</div>

## 使用建议（更容易算得稳）

- 时间步长：页面会给出稳定性推荐 $dt$（CFL 与扩散限制）；当你提高 Re 或加密网格时，建议同步减小 $dt$。
- 网格数：低网格（如 40×40 / 60×60）适合快速试验；高网格更能解析涡结构，但计算耗时明显上升。
- 压力求解器：
	- Jacobi：稳但慢；不涉及 $\omega$。
	- Gauss-Seidel：通常比 Jacobi 快；可视为 $\omega=1$。
	- SOR：合适的 $\omega$ 往往更快（常见 1.7–1.9 之间）。

## 部署说明

<div class="about-callout">
若使用 Streamlit Cloud（Community Cloud）部署：
<br/>- 平台为共享资源环境，计算速度可能随负载波动；连续多次高网格/长迭代会变慢属于常见现象。
<br/>- Linux 环境字体不一定包含 Times New Roman；项目已做字体回退以避免告警。
</div>

</div>
