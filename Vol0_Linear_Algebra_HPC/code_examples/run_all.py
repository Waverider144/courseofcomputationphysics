"""Run CPU validation and experiments. Execute from any working directory."""
import os
import tempfile
os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="vol0-mpl-"))
for key in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"):
    os.environ[key]="1"

from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from common import ROOT, environment, save
from sparse_linear_algebra import solvers, multilevel
from roofline import kernels, finite_volume
from fdtd import yee
from dg_fr import transport
from lbm import stream_collision


def figures(rows):
    directory=ROOT/"figures"; directory.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})
    intensity=np.logspace(-2,3,300)
    fig,ax=plt.subplots(figsize=(7,3.7))
    ax.loglog(intensity,np.minimum(1000,100*intensity),label="Hypothetical: 1000 GFLOP/s, 100 GB/s")
    ax.axvline(10,color="gray",linestyle=":")
    for name,i in (("CSR ~5/row ideal",10/(5*12+20)),("Yee two-phase",42/144),("GEMM n=256 ideal",256/12)):
        ax.scatter([i],[min(1000,100*i)],s=25)
        ax.annotate(name,(i,min(1000,100*i)),xytext=(5,-17),textcoords="offset points",fontsize=8)
    ax.set(xlabel="Modeled FLOP/byte",ylabel="GFLOP/s bound",title="Illustrative roof; not calibrated to this host")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(directory/"roofline_model.pdf"); plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9,3.5))
    wave=[r for r in rows if r["name"]=="yee_wave"]
    axes[0].loglog([r["parameters"]["n"] for r in wave],[r["error_e_L2"] for r in wave],"o-",label="Yee E-field")
    axes[0].set(xlabel="Points per direction",ylabel="L2 error",title="Periodic Maxwell, T=0.5")
    axes[0].legend()
    for p in (1,2,3):
        selected=[r for r in rows if r["name"]=="dg_transport" and r["parameters"]["p"]==p]
        axes[1].loglog([r["parameters"]["n"] for r in selected],[r["error_L2"] for r in selected],"o-",label=f"DG p={p}")
    axes[1].set(xlabel="Elements",ylabel="L2 error",title="Periodic transport, T=0.15"); axes[1].legend()
    fig.tight_layout(); fig.savefig(directory/"convergence.pdf"); plt.close(fig)
    chosen=[r for r in rows if r.get("gflops_model") is not None]
    fig,ax=plt.subplots(figsize=(8,4))
    ax.barh([r["name"]+(" p="+str(r["parameters"]["p"]) if "p" in r["parameters"] else "") for r in chosen],
            [r["gflops_model"] for r in chosen])
    ax.set(xscale="log",xlabel="Modeled GFLOP/s (different kernels; not a method ranking)",
           title="Measured CPU times with explicitly modeled work")
    fig.tight_layout(); fig.savefig(directory/"cpu_kernels.pdf"); plt.close(fig)


def main():
    checks=solvers.math_checks()
    checks["yee_constraints"]=yee.constraint_check()
    rows=[]
    for name,module in (("sparse",solvers),("multilevel",multilevel),("kernels",kernels),
                        ("Yee",yee),("DG/FVM",transport),("LBM",stream_collision),
                        ("FVM/FEM",finite_volume)):
        part=module.run(); rows.extend(part)
        print(f"{name}: {len(part)} experiments passed",flush=True)
    save("validation.json",{"status":"passed","mathematical_checks":checks,
         "experiment_count":len(rows),"all_runtime_assertions_passed":True})
    save("measurements.json",{"environment":environment(),"measurements":rows,
         "timing_scope":"See per-record scope; setup and diagnostics excluded unless stated",
         "traffic_warning":"All bytes are models, no DRAM hardware counters were used."})
    figures(rows)
    print("CPU experiment records and figures generated.",flush=True)


if __name__=="__main__":
    main()
