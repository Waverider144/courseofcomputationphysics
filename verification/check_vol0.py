"""Structural, preservation, mathematical, result-consistency and PDF checks for Volume 0."""
import json
from pathlib import Path
import re
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BOOK=ROOT/"Vol0_Linear_Algebra_HPC"
sys.path.insert(0,str(BOOK/"code_examples"))
from sparse_linear_algebra.solvers import math_checks
from fdtd.yee import constraint_check


def main():
    sources=sorted((BOOK/"chapters").glob("*/*.tex"))
    assert len(sources)==29
    counts={"chapters":29,"summaries":0,"author_supplements":0,"AI_boxes":0}
    referenced=set(); labels=set()
    for n,path in enumerate(sources,1):
        text=path.read_text()
        assert text.count(r"\chapter{")==1
        assert r"\label{v0ch:"+str(n)+"}" in text
        assert len(text)>1300,(n,"chapter too short")
        for token in (r"\learninggoals{",r"\paragraph{核心问题}",r"\costnote{",
                      r"\conceptbridge{",r"\aiexercise{",r"\studyroute{",r"\cite{"):
            assert token in text,(n,token)
        counts["summaries"]+=text.count(r"\begin{chaptersummary}")
        counts["author_supplements"]+=text.count(r"\conceptbridge{")
        counts["AI_boxes"]+=text.count(r"\aiexercise{")
        referenced.update(key for group in re.findall(r"\\cite\{([^}]+)\}",text) for key in group.split(","))
        labels.update(re.findall(r"\\label\{([^}]+)\}",text))
        assert "待补充" not in text and "本书不是" not in text
    bibliography=(BOOK/"references/bibliography.tex").read_text()
    keys=re.findall(r"\\bibitem\{([^}]+)\}",bibliography)
    assert len(keys)==len(set(keys))
    assert referenced<=set(keys),referenced-set(keys)
    checks=math_checks();checks["yee"]=constraint_check()
    result=json.loads((BOOK/"results/measurements.json").read_text())
    rows=result["measurements"]
    assert len(rows)==41
    assert all(r["seconds"]>0 and r["dram_bytes_measured"] is None for r in rows)
    assert all(r.get("relative_residual",0)<1.2e-9 for r in rows)
    cpu_dg={ (r["parameters"]["n"],r["parameters"]["p"]):r for r in rows if r["name"]=="dg_transport"}
    cpu_yee={r["parameters"]["n"]:r for r in rows if r["name"]=="yee_wave"}
    hardware={}
    for filename in ("hardware_local.json","hardware_remote.json"):
        path=BOOK/"results"/filename
        if not path.exists():
            hardware[filename]="not executed"
            continue
        data=json.loads(path.read_text())
        assert data["all_executed_checks_passed"],filename
        assert len(data["measurements"])==14
        for row in data["measurements"]:
            if row.get("case")=="full_yee":
                np.testing.assert_allclose(row["error_E_L2"],cpu_yee[row["n"]]["error_e_L2"],rtol=2e-10)
                assert row["divB_max"]<1e-11 and row["modified_energy_relative_drift"]<1e-11
                assert row["flops_model"]==30*row["n"]**3*row["steps"]
            if row.get("case")=="full_dg":
                np.testing.assert_allclose(row["error_L2"],cpu_dg[(row["elements"],row["p"])]["error_L2"],rtol=2e-9)
                assert row["mass_drift"]<1e-11
            if row["status"]=="executed_gpu":
                assert row["max_cpu_difference"]<1e-10
                assert row["general_field_cpu_difference"]<1e-10
                assert row["seconds_with_transfers"]>=row["seconds_device_advance"]
                assert row["flops_model"]==30*row["n"]**3*row["steps"]
        hardware[filename]=len(data["measurements"])
    log=(BOOK/"build/main.log").read_text(errors="replace")
    assert not re.search(r"^!|Missing character|Overfull \\[hv]box|undefined|multiply defined",log,re.M)
    pdf=ROOT/"Course_of_Computational_Physics_Vol0.pdf"
    inputs=[*sources,BOOK/"main.tex",BOOK/"preamble.tex",
            BOOK/"references/bibliography.tex",BOOK/"appendices/reproducibility.tex",
            BOOK/"results/summary.tex"]
    assert pdf.stat().st_mtime>=max(path.stat().st_mtime for path in inputs),"PDF is stale"
    text=subprocess.check_output(["pdftotext",str(pdf),"-"],text=True)
    for title in ("数值线性代数与现代高性能计算","本章总结","参考文献","本次运行的数值记录"):
        assert title in text,title
    report={"status":"passed",**counts,"references":len(keys),
            "CPU_experiments":len(rows),
            "hardware_records":hardware,"mathematical_checks":checks}
    (BOOK/"results/consistency.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
