"""Compile and validate optional hardware examples; outputs are local to the supplied workspace."""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone


def invoke(command, env, timeout=90):
    try:
        result=subprocess.run(command,env=env,capture_output=True,text=True,timeout=timeout)
        return {"command":command,"returncode":result.returncode,
                "stdout":result.stdout,"stderr":result.stderr}
    except (OSError,subprocess.TimeoutExpired) as error:
        return {"command":command,"returncode":None,"stdout":"","stderr":str(error)}


def portable_record(report, workspace, project):
    replacements = [(str(workspace), "<WORKSPACE>"), (str(project), "<SOURCE>"),
                    (socket.gethostname(), "<HOST>")]
    replacements.sort(key=lambda pair: len(pair[0]), reverse=True)

    def clean(value):
        if isinstance(value, dict):
            return {key: clean(item) for key, item in value.items()}
        if isinstance(value, list):
            return [clean(item) for item in value]
        if isinstance(value, str):
            for source, target in replacements:
                value = value.replace(source, target)
        return value

    public = clean(report)
    public["host"] = "remote" if report["remote"] else "local"
    return public


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--workspace",type=Path)
    parser.add_argument("--remote",action="store_true")
    parser.add_argument("--allowed-root",type=Path,
                        help="Authorized parent directory; required with --remote")
    parser.add_argument("--gpu-index",default="0")
    parser.add_argument("--gpu-arch",default="native")
    args=parser.parse_args()
    if args.remote and (args.workspace is None or args.allowed_root is None):
        parser.error("--remote requires --workspace and --allowed-root")
    project=Path(__file__).resolve().parents[1]
    workspace=(args.workspace or project).resolve()
    if args.remote:
        allowed=args.allowed_root.expanduser().resolve()
        if allowed not in workspace.parents:
            raise ValueError("Remote workspace must be a child of the authorized Tmp root")
    build=workspace/"build"; results=workspace/"results"; cache=workspace/"cache"
    for directory in (build,results,cache):
        directory.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy()
    env.update({"CCACHE_DISABLE":"1","CCACHE_DIR":str(cache/"ccache"),
                "CUDA_CACHE_PATH":str(cache/"cuda"),"TMPDIR":str(cache),
                "MPLCONFIGDIR":str(cache/"matplotlib"),"PYTHONDONTWRITEBYTECODE":"1",
                "OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1","MKL_NUM_THREADS":"1",
                "CUDA_VISIBLE_DEVICES":args.gpu_index})
    env["OMPI_MCA_orte_tmpdir_base"]=str(cache)
    cuda=Path(shutil.which("nvcc") or "/usr/local/cuda/bin/nvcc")
    if not args.remote:
        env["I_MPI_FABRICS"]="shm"
    report={"host":socket.gethostname(),"workspace":str(workspace),
            "utc":datetime.now(timezone.utc).isoformat(),"remote":args.remote,
            "gpu_index":args.gpu_index,"commands":[],"measurements":[],
            "scope":"same-host MPI; shared GPU short tests, no cross-node scaling"}
    for command in (["nvidia-smi","--query-gpu=name,memory.total,memory.used,utilization.gpu,driver_version",
                     "--format=csv,noheader"],[str(cuda),"--version"],["mpirun","--version"]):
        report["commands"].append(invoke(command,env))
    source=project/"code_examples"
    command=[str(cuda),"-arch="+args.gpu_arch,"-ccbin","/usr/bin/g++","-O3","-std=c++17",
             str(source/"gpu/yee_layout.cu"),"-o",str(build/"yee_layout")]
    compiled=invoke(command,env); report["commands"].append(compiled)
    if compiled["returncode"] and "rsqrt" in compiled["stderr"]:
        command[1:1]=["-U_GNU_SOURCE","-D_DEFAULT_SOURCE"]
        compiled=invoke(command,env);report["commands"].append(compiled)
    if compiled["returncode"]==0:
        for n in (32,64):
            report["commands"].append(invoke([str(build/"yee_layout"),str(n)],env))
    for filename,executable in (("halo.cpp","halo"),("yee.cpp","yee_mpi"),
                                ("dg_transport.cpp","dg_mpi")):
        command=["mpicxx","-O3","-std=c++17",str(source/"mpi"/filename),"-o",str(build/executable)]
        compiled=invoke(command,env);report["commands"].append(compiled)
        if compiled["returncode"]==0:
            cases=([["32"]] if executable=="halo" else
                   [["12"],["24"]] if executable=="yee_mpi" else [["8","3"],["16","3"]])
            for ranks in (1,2):
                for parameters in cases:
                    report["commands"].append(invoke(
                        ["mpirun","-n",str(ranks),str(build/executable),*parameters],env))
    for command in report["commands"]:
        if command["returncode"]==0:
            for line in command["stdout"].splitlines():
                if line.startswith("{"):
                    report["measurements"].append(json.loads(line))
    measured=report["measurements"]
    report["expected_measurements"]=14
    report["all_executed_checks_passed"]=len(measured)==14 and all(
        command["returncode"]==0 for command in report["commands"]
        if command["command"][0].endswith("mpirun") or
           command["command"][0].endswith("yee_layout"))
    output=results/("hardware_remote.json" if args.remote else "hardware_local.json")
    output.write_text(json.dumps(portable_record(report,workspace,project),indent=2)+"\n")
    print(json.dumps({"output":str(output),"measurements":len(measured),
                      "checks_passed":report["all_executed_checks_passed"]}),flush=True)
    for row in measured:
        print(json.dumps(row),flush=True)
    # Unavailable hardware is explicitly represented, not silently counted as passed.
    if not measured or not report["all_executed_checks_passed"]:
        sys.exit(1)


if __name__=="__main__":
    main()
