"""Fixed symmetric geometric V cycle and a two-level smoothed-aggregation model."""
import numpy as np
from scipy.sparse import diags, csr_matrix, eye
from scipy.sparse.linalg import splu, LinearOperator, cg
from common import timed, record, relative_residual


def poisson1(n):
    return diags([-np.ones(n-1),2*np.ones(n),-np.ones(n-1)], [-1,0,1], format="csr")


def prolongation(n):
    nc = (n-1)//2
    rows, cols, values = [], [], []
    for j in range(nc):
        for i, value in ((2*j,.5),(2*j+1,1.),(2*j+2,.5)):
            rows.append(i); cols.append(j); values.append(value)
    return csr_matrix((values,(rows,cols)), shape=(n,nc))


def smoother(a, rhs, x, steps=2):
    for _ in range(steps):
        x = x + (2/3)*(rhs-a@x)/a.diagonal()
    return x


def hierarchy(a):
    matrices, ps = [a], []
    while a.shape[0] > 7:
        p = prolongation(a.shape[0])
        a = (p.T@a@p).tocsr()
        ps.append(p); matrices.append(a)
    coarse = splu(a.tocsc())
    def cycle(level, rhs):
        if level == len(matrices)-1:
            return coarse.solve(rhs)
        current, p = matrices[level], ps[level]
        x = smoother(current,rhs,np.zeros_like(rhs))
        x += p @ cycle(level+1, p.T@(rhs-current@x))
        return smoother(current,rhs,x)
    return matrices, LinearOperator(matrices[0].shape, matvec=lambda r: cycle(0,r))


def aggregate(a):
    n = a.shape[0]
    # Adjacent pairs on the 1D path graph; no production strength heuristic.
    p0 = csr_matrix((np.ones(n), (np.arange(n),np.arange(n)//2)), shape=(n,(n+1)//2))
    p = ((eye(n)- (2/3)*diags(1/a.diagonal())@a)@p0).tocsr()
    ac = (p.T@a@p).tocsr()
    coarse = splu(ac.tocsc())
    def apply(rhs):
        x = smoother(a,rhs,np.zeros_like(rhs))
        x += p @ coarse.solve(p.T@(rhs-a@x))
        return smoother(a,rhs,x)
    return [a,ac], LinearOperator(a.shape, matvec=apply)


def run():
    results = []
    for n in (63,127):
        a = poisson1(n)
        rng = np.random.default_rng(n)
        rhs = a @ rng.normal(size=n)
        for name, builder in (("geometric_vcycle",hierarchy),("aggregation_two_level",aggregate)):
            (levels, pre), setup = timed(lambda: builder(a), repeats=3)
            # Check the entire fixed inverse action, not only coarse SPD.
            explicit = np.column_stack([pre@np.eye(n)[:,j] for j in range(n)])
            np.testing.assert_allclose(explicit,explicit.T,rtol=1e-11,atol=2e-12)
            assert np.linalg.eigvalsh(explicit).min() > 0
            def solve(monitor_residual=True):
                residuals = []
                x, flag = cg(a,rhs,M=pre,rtol=1e-10,atol=0,maxiter=1000,
                    callback=lambda x:residuals.append(relative_residual(a,x,rhs) if monitor_residual else None))
                return x,flag,residuals
            (x,flag,counted), timing = timed(lambda:solve(False),repeats=3)
            _,checked_flag,hist=solve(True)
            assert checked_flag==flag and len(hist)==len(counted)
            assert flag == 0 and relative_residual(a,x,rhs)<1.1e-10
            results.append(record(name,timing,{"N":n,"rtol":1e-10,"pre_sweeps":2,"post_sweeps":2,
                "omega":2/3},setup_seconds=setup["seconds"],iterations=len(hist),history=hist,
                relative_residual=relative_residual(a,x,rhs),
                timing_scope="solve with iteration counter; residual history and SPD checks are untimed",
                grid_complexity=sum(v.shape[0] for v in levels)/n,
                operator_complexity=sum(v.nnz for v in levels)/a.nnz,
                inverse_action_min_eigenvalue=float(np.linalg.eigvalsh(explicit).min())))
    return results
