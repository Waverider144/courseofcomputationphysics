# 数值线性代数与现代高性能计算

五部分、29 章的第 0 卷。中文入口为 [main.tex](main.tex)，英文入口为 [英文主文件](../Course_of_Computational_Physics_Vol0_EN.tex)。两种语言共用本目录下的示例、图和测量数据。

在仓库根目录执行：

```sh
make vol0 vol0-en
make check
```

## 示例索引

下列路径均相对于 code_examples/：

| 文件 | 内容 |
| --- | --- |
| sparse_linear_algebra/solvers.py | LU、稀疏 LU、CG/GMRES/BiCGSTAB、ILU、Poisson 收敛与手算核验 |
| sparse_linear_algebra/multilevel.py | 几何 V-cycle 与两层平滑聚合 |
| roofline/kernels.py | GEMM、CSR-SpMV、三维七点 stencil |
| roofline/finite_volume.py | 面邻接 FVM、P1 FEM 装配与矩阵自由对照 |
| fdtd/yee.py | 三维周期 Maxwell、交错能量、散度和关联矩阵 |
| dg_fr/transport.py | 高阶周期输运、FVM 对照与张量导数 |
| lbm/stream_collision.py | D2Q9 push/pull、AoS/SoA 与 BGK 演化 |
| gpu/yee_layout.cu | CUDA 全场 Yee、一般场 CPU 对照与布局基准 |
| mpi/halo.cpp | 阻塞与非阻塞 slab halo |
| mpi/yee.cpp | 两相 halo 的 Maxwell 推进与约束诊断 |
| mpi/dg_transport.cpp | 逐阶段迹交换的高阶 DG/RK4 |

## 数据与复现

[measurements.json](results/measurements.json) 保存 CPU 记录；硬件记录分别位于 [本机数据](results/hardware_local.json) 和 [远端数据](results/hardware_remote.json)。[validation.json](results/validation.json) 保存数值断言，[consistency.json](results/consistency.json) 保存文档与数据的一致性结果。

实测时间、工作量模型和计时范围分别记录。Python Yee 按 42 FLOPs/胞元整步计数；均匀网格 CUDA/MPI 融合更新按 30 FLOPs 计数。GPU 设备推进与含传输时间分别报告，MPI 数据对应单主机的一、两进程运行。

[实验指南](../docs/experiments.md) 给出依赖、命令、编译配置、远端工作目录约束及数据解释方法。
