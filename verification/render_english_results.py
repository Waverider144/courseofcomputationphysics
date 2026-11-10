"""Render English experiment tables from the shared measured JSON; no new benchmarks."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"Vol0_Linear_Algebra_HPC/results"
OUT=ROOT/"Vol0_Linear_Algebra_HPC_EN/appendices/results.tex"


def main():
    data=json.loads((DATA/"measurements.json").read_text())
    lines=[r"\section{Recorded Numerical Results}",
        "These tables are generated from the shared JSON records, not from new runs. "
        "CPU: Intel Core Ultra 7 155H; NumPy "+data["environment"]["numpy"]+
        "; SciPy "+data["environment"]["scipy"]+". Double precision and single-thread BLAS. "
        "Times describe these implementations and small workloads.",
        r"\begin{center}\small\begin{tabular}{lrrrrr}\toprule",
        r"Case & Cells/elements & $p$ & Steps & $L^2$ error & Advance/s\\\midrule"]
    for row in data["measurements"]:
        if row["name"] not in ("yee_wave","dg_transport","fvm_transport"):
            continue
        p=row["parameters"]
        name={"yee_wave":"Yee","dg_transport":"DG","fvm_transport":"FVM"}[row["name"]]
        error=row.get("error_e_L2",row.get("error_L2"))
        lines.append(f"{name} & {p['n']} & {p.get('p','--')} & {p['steps']} & "
                     f"{error:.3e} & {row['seconds']:.3e}"+r"\\")
    lines += [r"\bottomrule\end{tabular}\end{center}",
        "Yee uses $T=0.5$; DG/FVM use $T=0.15$. DG and FVM errors compare reconstructed "
        "fields against exact fields by integration. FVM cell-average error is also stored. "
        "Errors and times for different equations are interpreted separately."]
    reports=[json.loads((DATA/name).read_text()) for name in
             ("hardware_local.json","hardware_remote.json") if (DATA/name).exists()]
    if reports:
        lines += [r"\section{GPU and MPI Records}",
            "GPU kernels use constant-coefficient fusion: 30 FLOPs per cell-step. "
            "Device advance and transfer-inclusive times are separate. Both grids use 30 steps "
            "but different final times; their error ratio is not a convergence-order estimate. "
            "Remote GPU timings are short shared-load validation runs.",
            r"\begin{center}\small\begin{tabular}{lrrrrr}\toprule",
            r"Device & $n$ & $T$ & Kernel/s & With transfers/s & CPU max.\ difference\\\midrule"]
        for report in reports:
            host="GK RTX 4090" if report["remote"] else "Local RTX 500 Ada"
            for row in report["measurements"]:
                if row["status"]=="executed_gpu":
                    lines.append(f"{host} & {row['n']} & {row['T']:.4f} & "
                        f"{row['seconds_device_advance']:.3e} & {row['seconds_with_transfers']:.3e} & "
                        f"{row['max_cpu_difference']:.2e}"+r"\\")
        lines += [r"\bottomrule\end{tabular}\end{center}",
            "MPI runs use one host, include halos, and do not measure cross-node scaling.",
            r"\begin{center}\small\begin{tabular}{llrrrr}\toprule",
            r"Host & Case & Cells/elements & Ranks & $L^2$ error & Max.\ rank time/s\\\midrule"]
        for report in reports:
            host="GK" if report["remote"] else "Local"
            for row in report["measurements"]:
                if row.get("case") in ("full_yee","full_dg") and row["ranks"]==2:
                    case="Yee" if row["case"]=="full_yee" else "DG($p=3$)"
                    n=row.get("n",row.get("elements"))
                    error=row.get("error_E_L2",row.get("error_L2"))
                    lines.append(f"{host} & {case} & {n} & 2 & {error:.3e} & "
                                 f"{row['max_rank_seconds']:.3e}"+r"\\")
        lines += [r"\bottomrule\end{tabular}\end{center}",
            "The hardware JSON files retain one-/two-rank records, conservation, and constraints. "
            "No DRAM counters or calibrated roofs were used; semantic traffic and ideal reuse "
            "are separate models in the main text."]
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text("\n".join(lines)+"\n")


if __name__=="__main__":
    main()
