# Course of Computational Physics

Initialized by Harvey Tan

## EN Version

- Volume 1: [LaTeX source](CourseofComputationPhysics_Vol1_EN.tex).

As an engineer who regards Lev Landau as a role model, I have long felt that there is no Computational Physics textbook quite like the classic *Course of Theoretical Physics* by Landau and Lifshitz. Meanwhile, a friend of mine—who has a background in pure mathematics but is a novice in physics—expressed interest in the field and asked me for advice on getting started. That was the spark that ignited this project.

My goal is to craft a modern textbook tailored for the AI era. In this vision, complex derivations and low-level details act like "APIs"—tools that need not be memorized—allowing learners to focus on mastering the field's underlying principles and main paradigms. Think of this book as a quick-start guide to help you "launch your own kernel."

However, given my focus on CFD, CEM, and Plasma Physics, key areas such as first-principles calculations, nonlinear continuum mechanics, and explosion mechanics are beyond my current scope and remain unaddressed. I warmly welcome contributions and insights from experts across these diverse fields to help complete the picture.

## CN Version

中文版分为两卷，可分别使用 XeLaTeX 编译：

- 第一卷：从粒子到计算网格，建立从多粒子模型到离散方程和求解器的计算力学知识链。 [阅读 PDF](CourseofComputationPhysics_Vol1_CN.pdf) · [LaTeX 源码](CourseofComputationPhysics_Vol1_CN.tex)
- 第二卷：从洛伦兹协变到双曲守恒律，以 Maxwell 方程为例，深入讨论几何结构、约束传播、双曲系统及 DG 离散。 [阅读 PDF](CourseofComputationPhysics_Vol2_CN.pdf) · [LaTeX 源码](CourseofComputationPhysics_Vol2_CN.tex)

两卷的学习提示分别提供概念衔接、自测和可交给 AI 展开的具体问题。第一卷作者补充框中的文字为可继续修订的草稿。

### 编译中文版

安装包含 `ctex`、`tcolorbox` 和 `pgfplots` 等宏包的 TeX 发行版后，在项目目录运行：

```sh
xelatex CourseofComputationPhysics_Vol1_CN.tex
xelatex CourseofComputationPhysics_Vol1_CN.tex
xelatex CourseofComputationPhysics_Vol2_CN.tex
xelatex CourseofComputationPhysics_Vol2_CN.tex
```

每卷运行两次以生成目录和交叉引用。

作为一名将列夫·朗道视为偶像的工程师，我长期以来一直觉得，在计算物理学领域，缺少一部能与朗道和栗弗席兹（Lifshitz）经典的《理论物理学教程》相媲美的教材。与此同时，我的一位有着纯数学背景、但在物理领域尚属新手的朋友对该领域产生了兴趣，并向我寻求入门建议。这便成为了启动该项目的契机。

我的目标是打造一部面向 AI 时代的现代计算物理教程。在这一构想中，复杂的数学推导与底层细节被视为类似“API”的存在——它们是供调用的工具，而非需要死记硬背的负担，从而让学习者能够专注于掌握该领域的核心原理与主流范式。你可以将本书视为一本快速入门指南，帮助你“发射属于你自己的Kernel”。

不过，受限于我个人主要专注于计算流体力学、计算电磁学及等离子体物理，诸如第一性原理计算、非线性连续介质力学和爆炸力学等关键领域目前超出了我的知识范围，尚未纳入其中。我真诚地欢迎来自这些及更多不同领域的专家与同行贡献洞见、协同完善。

## Acknowledgement

Thanks to GPT, my Lifshitz, my best assistant, transforming my idea to reality
