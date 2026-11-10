"""Permuted nonuniform finite-volume adjacency and a P1 FEM operator comparison."""
import numpy as np
from scipy.sparse import diags
from common import timed, record


def run():
    rng=np.random.default_rng(144); n=4096
    volumes=rng.uniform(.5,1.5,size=n); volumes/=volumes.sum()
    order=rng.permutation(n); values=rng.normal(size=n)
    stored=np.empty(n); stored[order]=values
    widths=np.empty(n); widths[order]=volumes
    left=order; right=np.roll(order,-1)
    def face_operator():
        flux=stored[left]
        result=np.zeros(n)
        np.add.at(result,left,-flux/widths[left])
        np.add.at(result,right,flux/widths[right])
        return result
    out,timing=timed(face_operator)
    reference=-(values-np.roll(values,1))/volumes
    np.testing.assert_allclose(out[order],reference,atol=1e-10)
    mass_rate=float(widths@out)
    assert abs(mass_rate)<1e-10
    rows=[record("fvm_permuted_faces",timing,
        {"N":n,"dofs":n,"faces":n,"order":1,"speed":1,"boundary":"periodic",
         "geometry":"nonuniform 1D ring with permuted cell indices"},
         mass_rate=mass_rate,flops_model_note="not counted: gather, temporaries and accumulation separate")]
    h=1/(n+1)
    a=diags([-np.ones(n-1),2*np.ones(n),-np.ones(n-1)],[-1,0,1],format="csr")/h
    u=rng.normal(size=n)
    def matrix_free():
        padded=np.pad(u,1)
        jump=(padded[:-1]-padded[1:])/h
        result=np.zeros(n+2)
        result[:-1]+=jump;result[1:]-=jump
        return result[1:-1]
    assembled,t1=timed(lambda:a@u)
    free,t2=timed(matrix_free)
    np.testing.assert_allclose(assembled,free,rtol=1e-12,atol=1e-11)
    rows.extend([record("fem_p1_assembled",t1,{"N":n,"dofs":n,"order":1,"nnz":a.nnz}),
                 record("fem_p1_matrix_free",t2,{"N":n,"dofs":n,"order":1})])
    return rows
