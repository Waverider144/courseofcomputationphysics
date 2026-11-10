# 计算物理学简明教程

[English](README.md) | **简体中文**

由 Harvey Tan 发起。

本教程面向具有数学基础的读者，以简明的知识链连接物理建模、数值算法与可复现计算。三卷依次联系模型假设、偏微分方程结构、离散方法、矩阵求解和现代计算机体系结构。

## 阅读教材

| 卷册 | 中文 PDF | 英文 PDF | 中文源码 | 英文源码 |
| --- | --- | --- | --- | --- |
| 第 0 卷：数值线性代数与现代高性能计算 | [阅读](Course_of_Computational_Physics_Vol0.pdf) | [阅读](Course_of_Computational_Physics_Vol0_EN.pdf) | [LaTeX](Vol0_Linear_Algebra_HPC/main.tex) | [LaTeX](Course_of_Computational_Physics_Vol0_EN.tex) |
| 第 1 卷：从动力学约化到现代高阶离散 | [阅读](Course_of_Computational_Physics_Vol1_Revised.pdf) | [阅读](Course_of_Computational_Physics_Vol1_EN.pdf) | [LaTeX](Course_of_Computational_Physics_Vol1_Revised.tex) | [LaTeX](Course_of_Computational_Physics_Vol1_EN.tex) |
| 第 2 卷：从 Lorentz 协变性到双曲守恒律 | [阅读](CourseofComputationPhysics_Vol2_CN.pdf) | [阅读](CourseofComputationPhysics_Vol2_EN.pdf) | [LaTeX](CourseofComputationPhysics_Vol2_CN.tex) | [LaTeX](CourseofComputationPhysics_Vol2_EN.tex) |

### 第 0 卷

五部分、29 章，讨论矩阵结构、矩阵分解、Krylov 方法、预条件、多重网格与 Roofline 性能分析。Yee-FDTD、DG/FR、FEM、FVM 和 LBM 将求解器设计联系到具体离散算子，时间推进与并行通信进一步连接局部内核和总求解成本。

中英文版共用[配套代码](Vol0_Linear_Algebra_HPC/code_examples/)、[图表](Vol0_Linear_Algebra_HPC/figures/)和[测量记录](Vol0_Linear_Algebra_HPC/results/)。依赖、验证方法与计时约定见[实验指南](docs/experiments.md)。

### 第 1 卷

《计算物理学简明教程：从动力学约化到现代高阶离散》共六部分、22 章。从多粒子动力学出发，逐步建立统计描述、动理学方程、速度矩与连续介质闭合；再由函数空间和弱形式进入有限差分、有限体积、有限元、谱方法、DG、FR、VCJH 与 Mortar 耦合。LBM、稀薄气体、MHD、回旋动理学、网格与验证共同构成完整的建模链。

第 14 章将空间算子联系到 ADER、连续显式 Runge--Kutta（CERK）、守恒局部时间步进（LTS）与隐式--显式（IMEX）积分。离散后产生的代数求解问题在第 0 卷展开。

### 第 2 卷

以 Maxwell 方程为主线，将微分形式与 Lorentz 协变性联系到演化和约束、对称双曲性、能量估计、相容算子及高阶 DG 色散。第 5.5 节讨论 RK、保辛积分、ADER、CERK、LTS 与 IMEX；第 7 章及 Python 附录提供可复现的一维 DG 色散实验。

各卷英文版与中文版保持相同的章节结构、公式、参考文献和习题。

## 学习路线

章首总结说明当前主题在知识链中的位置，核心概念联系解释转向下一步的动机；检索关键词明确省略的推导与先备知识。具体的 AI 提问提供计算、算例、方法比较和实验的展开入口，模型假设与参考文献则为核验结果提供依据。

## 构建与校验

在仓库根目录执行：

```sh
make                     # 第 0、1 卷中英文版
make english             # 第 0、1 卷英文版
make check               # 数学、结构、数值与 PDF 校验
```

构建通过 latexmk 调用 XeLaTeX，生成第 1 卷术语索引，并将交付 PDF 放在仓库根目录。中间文件保存在各构建目录。

TeX 环境需包含 ctex 支持的中文字体、Latin Modern、babel、tcolorbox、pgfplots、listings、needspace 和 placeins。校验依赖 Python 3、NumPy、SciPy、qpdf 与 Poppler 工具。可选的 CUDA 和 MPI 工具链见[实验指南](docs/experiments.md)。

也可单独运行：

```sh
make vol0 vol0-en revised vol1-en
make verify vol0-verify math-verify translations-verify
```

第 2 卷单独构建：

```sh
latexmk -xelatex -outdir=build -interaction=nonstopmode -halt-on-error CourseofComputationPhysics_Vol2_CN.tex
latexmk -xelatex -outdir=build -interaction=nonstopmode -halt-on-error CourseofComputationPhysics_Vol2_EN.tex
```

## 计算实验

```sh
python -m pip install -r Vol0_Linear_Algebra_HPC/code_examples/requirements.txt
make vol0-examples        # CPU 实验、图表与中英文结果表
make vol0-hardware        # 可选 CUDA 与单主机 MPI 实验
```

这些目标会更新测量记录。计时结果注明硬件、实现和工作负载，模型 FLOPs、数据流量与实测时间分别记录。[代码索引](Vol0_Linear_Algebra_HPC/README.md)列出各示例对应的主题。

## 项目背景与贡献

本项目源于一位具有数学背景的朋友对物理学习路线的需求，也受到 Landau 与 Lifshitz《理论物理学教程》的启发。目前重点覆盖计算流体力学、计算电磁学与等离子体物理。

欢迎贡献推导、数值验证、术语、翻译或其他物理领域的内容。请保持简明结构，明确假设，并为新增技术内容提供参考文献。

## 致谢

感谢 GPT 协助将作者的构想整理为教材。
