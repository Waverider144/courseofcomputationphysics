"""Modal DG upwind transport, FVM comparison, and tensor-product volume kernels."""
from time import perf_counter
import numpy as np
from numpy.polynomial.legendre import leggauss, legvander, legder, legval
from common import timed, record


def rk4(u,dt,rhs):
    a=rhs(u); b=rhs(u+.5*dt*a); c=rhs(u+.5*dt*b); d=rhs(u+dt*c)
    return u+dt/6*(a+2*b+2*c+d)


def operators(p):
    q,w=leggauss(p+2); v=legvander(q,p)
    deriv=np.column_stack([legval(q,legder(np.eye(p+1)[j])) for j in range(p+1)])
    s=deriv.T@(w[:,None]*v)
    return s


def dg_run(n,p,final_time=.15):
    h=1/n; q,w=leggauss(max(p+3,8)); v=legvander(q,p)
    coordinates=(np.arange(n)[:,None]+(q+1)/2)*h
    initial=np.sin(2*np.pi*coordinates)
    coeff=(initial*w)@v*((2*np.arange(p+1)+1)/2)
    s=operators(p); left=(-1.)**np.arange(p+1)
    invmass=(2*np.arange(p+1)+1)/h
    def rhs(u):
        right=np.sum(u,axis=1)
        flux_left=np.roll(right,1)
        return (u@s.T-right[:,None]+flux_left[:,None]*left)*invmass
    steps=int(np.ceil(final_time/(.25*h/(2*p+1)**2))); dt=final_time/steps
    u=coeff.copy(); mass0=h*np.sum(u[:,0])
    start=perf_counter()
    for _ in range(steps):
        u=rk4(u,dt,rhs)
    elapsed=perf_counter()-start
    values=u@v.T
    exact=np.sin(2*np.pi*(coordinates-final_time))
    error=float(np.sqrt(.5*h*np.sum((values-exact)**2*w)))
    mass_drift=abs(h*np.sum(u[:,0])-mass0)
    assert mass_drift<1e-12
    return record("dg_transport",{"seconds":elapsed,"repeats":1,"warmup_calls":0},
        {"n":n,"p":p,"order":p+1,"dofs":n*(p+1),"h":h,"dt":dt,
         "steps":steps,"stages":4,"T":final_time,"boundary":"periodic","flux":"upwind",
         "quadrature":len(q)},error_L2=error,mass_drift=mass_drift,
         kernel_scope="projection and diagnostics excluded; RK4 allocations included")


def fvm_run(n,final_time=.15):
    h=1/n; x=(np.arange(n)+.5)*h
    # Exact initial cell averages; compare to exact cell averages at T.
    u=np.sin(2*np.pi*x)*np.sinc(h)
    steps=int(np.ceil(final_time/(.4*h))); dt=final_time/steps
    mass=h*np.sum(u)
    start=perf_counter()
    for _ in range(steps):
        u=u-dt/h*(u-np.roll(u,1))
    elapsed=perf_counter()-start
    exact=np.sin(2*np.pi*(x-final_time))*np.sinc(h)
    error=float(np.sqrt(h*np.sum((u-exact)**2)))
    q,w=leggauss(8)
    points=(np.arange(n)[:,None]+(q+1)/2)*h
    reconstructed_error=float(np.sqrt(.5*h*np.sum(
        (u[:,None]-np.sin(2*np.pi*(points-final_time)))**2*w)))
    assert abs(h*np.sum(u)-mass)<1e-12
    return record("fvm_transport",{"seconds":elapsed,"repeats":1,"warmup_calls":0},
        {"n":n,"p":0,"order":1,"dofs":n,"h":h,"dt":dt,"steps":steps,"stages":1,
         "T":final_time,"boundary":"periodic","flux":"upwind"},
        error_cell_average_L2=error,error_L2=reconstructed_error,
        mass_drift=float(abs(h*np.sum(u)-mass)),
        error_norm_note="error_L2 compares piecewise-constant reconstructed field to exact field, as for DG")


def tensor_run(p):
    n=p+1; rng=np.random.default_rng(p)
    d=rng.normal(size=(n,n)); u=rng.normal(size=(n,n,n))
    def volume():
        return np.array([np.einsum("il,ljk->ijk",d,u,optimize=True),
                         np.einsum("jl,ilk->ijk",d,u,optimize=True),
                         np.einsum("kl,ijl->ijk",d,u,optimize=True)])
    result,timing=timed(volume,repeats=7)
    identity=np.eye(n)
    reference=np.array([np.kron(np.kron(d,identity),identity)@u.ravel(),
                        np.kron(np.kron(identity,d),identity)@u.ravel(),
                        np.kron(np.kron(identity,identity),d)@u.ravel()]).reshape(3,n,n,n)
    np.testing.assert_allclose(result,reference,atol=1e-12)
    return record("tensor_volume",timing,{"p":p,"n":n,"dofs":n**3,"directions":3},
        3*n**3*(2*n-1),32*n**3+8*n*n,
        bytes_model_kind="one input read, three derivative writes, one D read; ideal reuse")


def run():
    rows=[]
    for p in (1,2,3):
        coarse=dg_run(8,p); fine=dg_run(16,p)
        ratio=coarse["error_L2"]/fine["error_L2"]
        assert ratio>2**(p+.6), (p,ratio)
        rows.extend([coarse,fine])
    for n in (32,64):
        rows.append(fvm_run(n))
    rows.extend(tensor_run(p) for p in (2,4,6))
    return rows
