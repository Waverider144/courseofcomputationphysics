"""Shared measurement schema; modeled traffic is never labeled measured DRAM."""
from pathlib import Path
from time import perf_counter
import json
import os
import platform
import statistics
import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def environment():
    cpu = platform.processor()
    info = Path("/proc/cpuinfo")
    if info.exists():
        for line in info.read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    return {
        "platform": platform.platform(), "cpu": cpu,
        "logical_cpus": os.cpu_count(),
        "affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "python": platform.python_version(),
        "numpy": np.__version__, "scipy": scipy.__version__, "dtype": "float64",
        "threads": {k: os.environ.get(k) for k in
                    ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
        "clock": "perf_counter", "dram_bytes_measured": None,
        "hardware_roofs_calibrated": False,
    }


def timed(call, repeats=5):
    call()
    samples = []
    result = None
    for _ in range(repeats):
        start = perf_counter()
        result = call()
        samples.append(perf_counter() - start)
    return result, {"seconds": statistics.median(samples), "minimum_seconds": min(samples),
                    "repeats": repeats, "warmup_calls": 1}


def record(name, timing, parameters, flops=None, traffic=None, **extra):
    seconds = timing["seconds"]
    return {
        "name": name, "status": "executed_cpu", **timing,
        "parameters": parameters, "dtype": "float64",
        "flops_model": flops, "bytes_model": traffic,
        "arithmetic_intensity_model": flops / traffic if flops and traffic else None,
        "gflops_model": flops / seconds / 1e9 if flops else None,
        "effective_GBps_model": traffic / seconds / 1e9 if traffic else None,
        "dram_bytes_measured": None, **extra,
        "seconds_per_step": seconds / parameters["steps"] if parameters.get("steps") else None,
        "time_to_solution_seconds": seconds + extra.get("setup_seconds", 0),
        "time_to_solution_scope": "measured solve/advance plus separately recorded setup; verification and IO excluded",
    }


def save(name, data):
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def relative_residual(a, x, b):
    return float(np.linalg.norm(b - a @ x) / max(np.linalg.norm(b), np.finfo(float).tiny))
