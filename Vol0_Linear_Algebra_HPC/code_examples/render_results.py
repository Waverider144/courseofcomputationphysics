"""Generate the typeset result snapshot from the actual JSON records."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]


def main():
    data=json.loads((ROOT/"results/measurements.json").read_text())
    rows=data["measurements"]
    lines=[r"\section{本次运行的数值记录}",
        "下表由 JSON 记录生成。CPU 环境为 Intel Core Ultra 7 155H，NumPy "
        +data["environment"]["numpy"]+"、SciPy "+data["environment"]["scipy"]
        +"，双精度、单线程 BLAS。时间仅代表这些实现和小规模工作负载。",
        r"\begin{center}\small",
        r"\begin{tabular}{lrrrrr}\toprule",
        r"案例 & 网格/单元数 & $p$ & 步数 & $L^2$ 误差 & 推进时间/s\\\midrule"]
    for row in rows:
        if row["name"] not in ("yee_wave","dg_transport","fvm_transport"):
            continue
        p=row["parameters"]
        name={"yee_wave":"Yee","dg_transport":"DG","fvm_transport":"FVM"}[row["name"]]
        error=row.get("error_e_L2",row.get("error_L2"))
        lines.append(f"{name} & {p['n']} & {p.get('p','--')} & {p['steps']} & "
                     +f"{error:.3e} & {row['seconds']:.3e}"+r"\\")
    lines.extend([r"\bottomrule\end{tabular}\end{center}",
        "Yee 的终止时间为 $T=0.5$，DG 与 FVM 为 $T=0.15$。"
        "DG 与 FVM 均以重构场对解析场的积分误差比较；另行保存 FVM 单元平均误差。"
        "不同方程的误差和时间分别解读。"])
    hardware=[]
    for name in ("hardware_local.json","hardware_remote.json"):
        path=ROOT/"results"/name
        if path.exists():
            hardware.append(json.loads(path.read_text()))
    if hardware:
        lines.extend([r"\section{GPU 与 MPI 执行记录}",
            "GPU 采用常系数融合更新（30 FLOPs/胞元整步）；设备推进与包含传输的时间分别报告。"
            "两种网格均固定 30 步，终止时间不同，故不由其误差比估计收敛阶。"
            "远端 GPU 为共享负载下的短时验证。"])
        lines += [r"\begin{center}\small\begin{tabular}{lrrrrr}\toprule",
            r"设备 & $n$ & $T$ & 核推进/s & 含传输/s & CPU 最大差\\\midrule"]
        for report in hardware:
            host="GK RTX 4090" if report["remote"] else "本机 RTX 500 Ada"
            for row in report["measurements"]:
                if row["status"]=="executed_gpu":
                    lines.append(f"{host} & {row['n']} & {row['T']:.4f} & "
                        f"{row['seconds_device_advance']:.3e} & {row['seconds_with_transfers']:.3e} & "
                        f"{row['max_cpu_difference']:.2e}"+r"\\")
        lines += [r"\bottomrule\end{tabular}\end{center}",
            "MPI 实验均在单一主机内运行，包含 halo 交换，不能用作跨节点扩展数据。",
            r"\begin{center}\small\begin{tabular}{llrrrr}\toprule",
            r"位置 & 案例 & 网格/单元数 & 进程 & $L^2$ 误差 & 最慢进程时间/s\\\midrule"]
        for report in hardware:
            host="GK" if report["remote"] else "本机"
            for row in report["measurements"]:
                if row.get("case") in ("full_yee","full_dg") and row["ranks"]==2:
                    case="Yee" if row["case"]=="full_yee" else "DG($p=3$)"
                    n=row.get("n",row.get("elements"))
                    error=row.get("error_E_L2",row.get("error_L2"))
                    lines.append(f"{host} & {case} & {n} & 2 & {error:.3e} & "
                                 f"{row['max_rank_seconds']:.3e}"+r"\\")
        lines += [r"\bottomrule\end{tabular}\end{center}",
            "一进程和两进程的完整记录、守恒与约束量见相应硬件 JSON。"
            "本次记录未使用 DRAM 计数器，也未标定硬件 Roofline；语义流量与理想复用估算在正文中单列。"]
    (ROOT/"results/summary.tex").write_text("\n".join(lines)+"\n")


if __name__=="__main__":
    main()
