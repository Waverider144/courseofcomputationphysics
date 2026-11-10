"""CPU kernels: modeled FLOPs/traffic, not a DRAM bandwidth calibration."""
import numpy as np
from scipy.sparse import diags, eye, kron
from common import timed, record


def run():
    rng=np.random.default_rng(2026)
    n=256
    a=rng.normal(size=(n,n)); b=rng.normal(size=(n,n))
    out,timing=timed(lambda:a@b,repeats=7)
    np.testing.assert_allclose(out[:2,:2],a[:2]@b[:,:2],rtol=1e-12,atol=1e-12)
    rows=[record("gemm",timing,{"n":n,"dofs":n*n,"operation":"C=A@B"},2*n**3,24*n*n,
                 bytes_model_kind="ideal three-array read/write; write allocation excluded")]
    n=128
    t=diags([-np.ones(n-1),2*np.ones(n),-np.ones(n-1)],[-1,0,1],format="csr")
    a=(kron(eye(n),t)+kron(t,eye(n))).tocsr()
    x=rng.normal(size=a.shape[0])
    out,timing=timed(lambda:a@x,repeats=7)
    q=a.data.nbytes+a.indices.nbytes+a.indptr.nbytes+x.nbytes+out.nbytes
    rows.append(record("csr_spmv",timing,{"n":n,"N":a.shape[0],"nnz":a.nnz,
        "index_bytes":a.indices.dtype.itemsize},2*a.nnz,q,
        bytes_model_kind="matrix once, x once, y write once; ideal cache reuse"))
    n=64; u=rng.normal(size=(n,n,n)); invh2=n*n
    def stencil():
        neighbors=sum(np.roll(u,shift,axis=axis) for axis in range(3) for shift in (-1,1))
        return (neighbors-6*u)*invh2
    result,timing=timed(stencil,repeats=5)
    # Independent scalar point check.
    i,j,k=7,11,13
    expected=(u[i-1,j,k]+u[i+1,j,k]+u[i,j-1,k]+u[i,j+1,k]+u[i,j,k-1]+u[i,j,k+1]-6*u[i,j,k])*n*n
    np.testing.assert_allclose(result[i,j,k],expected)
    rows.append(record("seven_point_stencil",timing,{"n":n,"dofs":n**3,"boundary":"periodic"},
        8*n**3,16*n**3,bytes_model_kind="ideal spatial reuse; NumPy roll/sum temporaries excluded",
        semantic_bytes=64*n**3))
    return rows
