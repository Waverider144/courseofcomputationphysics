"""Dense/sparse factorization and Krylov examples with independently checked residuals."""
from time import perf_counter
import numpy as np
from scipy import linalg
from scipy.sparse import diags, eye, kron
from scipy.sparse.linalg import cg, gmres, bicgstab, splu, spilu, LinearOperator
from common import timed, record, relative_residual


def poisson(n):
    t = diags([-np.ones(n-1), 2*np.ones(n), -np.ones(n-1)], [-1, 0, 1], format="csr")
    return (kron(eye(n), t) + kron(t, eye(n))).tocsr()


def arnoldi(a, r, m):
    v = np.zeros((len(r), m+1))
    h = np.zeros((m+1, m))
    v[:, 0] = r / np.linalg.norm(r)
    for j in range(m):
        w = a @ v[:, j]
        for i in range(j+1):
            h[i, j] = v[:, i] @ w
            w -= h[i, j] * v[:, i]
        h[j+1, j] = np.linalg.norm(w)
        if h[j+1, j] <= 1e-14:
            raise ArithmeticError("Invariant Krylov space reached in this teaching routine")
        v[:, j+1] = w / h[j+1, j]
    return v, h


def math_checks():
    a = np.array([[0,2,1,0], [4,4,0,1], [2,0,3,1], [0,1,1,2]], dtype=float)
    p = np.eye(4)[[1,0,2,3]]
    l = np.array([[1,0,0,0], [0,1,0,0], [.5,-1,1,0], [0,.5,.125,1]])
    u = np.array([[4,4,0,1], [0,2,1,0], [0,0,4,.5], [0,0,0,31/16]])
    np.testing.assert_allclose(p @ a, l @ u)
    b = a @ np.ones(4)
    y = linalg.solve_triangular(l, p @ b, lower=True, unit_diagonal=True)
    np.testing.assert_allclose(y, [9,3,4.5,31/16])
    np.testing.assert_allclose(linalg.solve_triangular(u, y), 1)
    v, h = arnoldi(a, np.eye(4)[:,0], 2)
    expected = np.array([[0,np.sqrt(5)], [2*np.sqrt(5),19/5], [0,7/5]])
    np.testing.assert_allclose(h, expected, atol=2e-15)
    np.testing.assert_allclose(v.T @ v, np.eye(3), atol=2e-15)
    np.testing.assert_allclose(a @ v[:,:2], v @ h, atol=2e-15)
    rhs = np.array([1.,0,0])
    coeff = np.linalg.lstsq(h, rhs, rcond=None)[0]
    np.testing.assert_allclose(coeff, [-95/348,25*np.sqrt(5)/174])
    np.testing.assert_allclose(np.linalg.norm(rhs-h@coeff), 7/np.sqrt(174))
    acg = np.array([[4.,1],[1,3]])
    r = np.array([1.,2]); direction = r.copy(); x = np.zeros(2)
    for k in range(2):
        ar = acg @ direction
        alpha = r @ r / (direction @ ar)
        x += alpha * direction
        new = r - alpha * ar
        beta = new @ new / (r @ r)
        direction = new + beta * direction
        r = new
    np.testing.assert_allclose(x, [1/11,7/11])
    # Exact-mass P1 FR correction equals nodal DG lifting.
    nodes = np.array([-1.,1.])
    mass = np.array([[2/3,1/3],[1/3,2/3]])
    np.testing.assert_allclose((3*nodes-1)/2, -np.linalg.solve(mass, [1,0]))
    np.testing.assert_allclose((3*nodes+1)/2, np.linalg.solve(mass, [0,1]))
    # P1 finite element assembly agrees with elementwise application.
    n = 9; hmesh = 1/(n+1); vec = np.arange(n, dtype=float)
    assembled = diags([-np.ones(n-1),2*np.ones(n),-np.ones(n-1)], [-1,0,1]) / hmesh
    padded = np.pad(vec, 1); out = np.zeros(n+2)
    for j in range(n+1):
        local = np.array([[1.,-1],[-1,1]]) @ padded[j:j+2] / hmesh
        out[j:j+2] += local
    np.testing.assert_allclose(out[1:-1], assembled @ vec)
    return {"lu_4x4": True, "arnoldi_2_steps": True, "gmres_small_ls": True,
            "cg_2_steps": True, "fr_p1_exact_mass_equivalence": True,
            "fem_assembled_matrix_free": True}


def run():
    rows = []
    rng = np.random.default_rng(2026)
    dense = rng.normal(size=(96,96)) + 96*np.eye(96)
    b = dense @ np.ones(96)
    factors, setup = timed(lambda: linalg.lu_factor(dense))
    x, solve = timed(lambda: linalg.lu_solve(factors, b))
    assert relative_residual(dense, x, b) < 1e-12
    rows += [record("dense_lu_setup", setup, {"N":96}, 2*96**3/3),
             record("dense_lu_solve", solve, {"N":96}, 2*96**2,
                    relative_residual=relative_residual(dense,x,b))]
    a = poisson(22); b = a @ rng.normal(size=a.shape[0])
    for ordering in ("NATURAL", "COLAMD"):
        factor, setup = timed(lambda: splu(a.tocsc(), permc_spec=ordering), repeats=3)
        x, solve = timed(lambda: factor.solve(b))
        assert relative_residual(a,x,b) < 1e-11
        parameters = {"N":a.shape[0], "nnz":a.nnz, "ordering":ordering,
                      "factor_nnz":factor.L.nnz + factor.U.nnz}
        rows.append(record("sparse_lu_"+ordering, solve, parameters,
                           setup_seconds=setup["seconds"], relative_residual=relative_residual(a,x,b)))
    for nonsymmetric in (False, True):
        matrix = a.copy()
        if nonsymmetric:
            # Upwind x advection on each grid row; zero Dirichlet boundary.
            up = diags([-np.ones(21),np.ones(22)], [-1,0], format="csr")
            matrix = matrix + 3*kron(eye(22), up, format="csr")
        rhs = matrix @ rng.normal(size=matrix.shape[0])
        ilu_start = perf_counter()
        ilu = spilu(matrix.tocsc(), drop_tol=1e-3, fill_factor=6)
        ilu_setup = perf_counter()-ilu_start
        pre = LinearOperator(matrix.shape, matvec=ilu.solve)
        methods = [("gmres", gmres, None), ("gmres_ilu", gmres, pre),
                   ("bicgstab", bicgstab, None)]
        if not nonsymmetric:
            methods.append(("cg", cg, None))
        for name, solver, precond in methods:
            def solve_once(monitor_residual=True):
                history = []
                if solver is gmres:
                    x, flag = solver(matrix, rhs, M=precond, rtol=1e-9, atol=0,
                                     restart=30, maxiter=100,
                                     callback=lambda value:history.append(value if monitor_residual else None),
                                     callback_type="pr_norm")
                else:
                    def monitor(xk):
                        history.append(relative_residual(matrix,xk,rhs) if monitor_residual else None)
                    x, flag = solver(matrix, rhs, M=precond, rtol=1e-9, atol=0,
                                     maxiter=2000, callback=monitor)
                return x, flag, history
            (x, flag, counted), timing = timed(lambda:solve_once(False), repeats=3)
            _, checked_flag, history = solve_once(True)
            assert checked_flag==flag and len(history)==len(counted)
            residual = relative_residual(matrix,x,rhs)
            assert flag == 0 and residual <= 1.1e-9, (name,flag,residual)
            rows.append(record(name+("_advection" if nonsymmetric else "_poisson"), timing,
                {"N":matrix.shape[0], "nnz":matrix.nnz, "rtol":1e-9, "restart":30 if solver is gmres else None,
                 "ordering":"COLAMD" if precond is not None else None},
                iterations=len(history), history=history, history_kind="preconditioned_callback" if solver is gmres else "true_residual",
                relative_residual=residual, setup_seconds=ilu_setup if precond is not None else 0,
                timing_scope="solve with iteration counter; residual-history reconstruction is untimed",
                factor_nnz=ilu.L.nnz+ilu.U.nnz if precond is not None else None))
    pde_errors=[]
    for n in (16,32):
        hmesh=1/(n+1)
        matrix=poisson(n)/hmesh**2
        axis=np.arange(1,n+1)*hmesh
        exact=np.outer(np.sin(np.pi*axis),np.sin(np.pi*axis)).ravel()
        rhs=2*np.pi**2*exact
        (answer,flag),timing=timed(lambda:cg(matrix,rhs,rtol=1e-12,atol=0))
        error=float(hmesh*np.linalg.norm(answer-exact))
        assert flag==0 and relative_residual(matrix,answer,rhs)<1.1e-12
        pde_errors.append(error)
        rows.append(record("poisson_pde_convergence",timing,
            {"n":n,"N":n*n,"dofs":n*n,"h":hmesh,"order":2,"rtol":1e-12,
             "boundary":"homogeneous Dirichlet"},
            error_L2=error,relative_residual=relative_residual(matrix,answer,rhs),
            rhs_kind="sampled continuous forcing, not A@exact"))
    assert 3.5<pde_errors[0]/pde_errors[1]<4.2
    return rows
