"""D2Q9 BGK with periodic boundaries and push/pull/layout equivalence checks."""
import numpy as np
from common import timed, record

C=np.array([[0,0],[1,0],[0,1],[-1,0],[0,-1],[1,1],[-1,1],[-1,-1],[1,-1]])
W=np.array([4/9]+[1/9]*4+[1/36]*4)


def equilibrium(rho,velocity):
    cu=np.einsum("qd,dij->qij",C,velocity)
    uu=np.sum(velocity*velocity,axis=0)
    return W[:,None,None]*rho*(1+3*cu+4.5*cu*cu-1.5*uu)


def stream_push(f):
    return np.array([np.roll(f[q],tuple(c),axis=(0,1)) for q,c in enumerate(C)])


def stream_pull(f):
    n=f.shape[1]; x=np.arange(n)
    return np.array([f[q][np.ix_((x-c[0])%n,(x-c[1])%n)] for q,c in enumerate(C)])


def stream_aos(f):
    out=np.empty_like(f)
    for q,c in enumerate(C):
        out[:,:,q]=np.roll(f[:,:,q],tuple(c),axis=(0,1))
    return out


def advance(f,tau):
    rho=np.sum(f,axis=0)
    velocity=np.einsum("qd,qij->dij",C,f)/rho
    return stream_push(f-(f-equilibrium(rho,velocity))/tau)


def run():
    n=48; rng=np.random.default_rng(9)
    raw=rng.random((9,n,n))
    push,t1=timed(lambda:stream_push(raw),repeats=7)
    pull,t2=timed(lambda:stream_pull(raw),repeats=7)
    aos=np.ascontiguousarray(np.moveaxis(raw,0,-1))
    out_aos,t3=timed(lambda:stream_aos(aos),repeats=7)
    np.testing.assert_array_equal(push,pull)
    np.testing.assert_array_equal(push,np.moveaxis(out_aos,-1,0))
    rows=[]
    for name,timing in (("lbm_stream_soa_push",t1),("lbm_stream_soa_pull",t2),("lbm_stream_aos_push",t3)):
        rows.append(record(name,timing,{"n":n,"Q":9,"steps":1,"dofs":9*n*n,"boundary":"periodic"},
            traffic=18*n*n*8,bytes_model_kind="two-buffer streaming read/write lower bound"))
    velocity=np.zeros((2,n,n))
    velocity[0]=.01*np.sin(2*np.pi*np.arange(n)/n)[None,:]
    f=equilibrium(np.ones((n,n)),velocity)
    initial=float(np.sum(f)); tau=.8; steps=20
    def solve():
        current=f.copy()
        for _ in range(steps):
            current=advance(current,tau)
        return current
    result,timing=timed(solve,repeats=3)
    drift=float(abs(np.sum(result)-initial)/initial)
    assert drift<1e-12 and np.isfinite(result).all()
    rows.append(record("lbm_collision_stream",timing,
        {"n":n,"Q":9,"dofs":9*n*n,"steps":steps,"tau":tau,"max_initial_speed":.01,
         "boundary":"periodic","dt_lattice":1},relative_mass_drift=drift,
        bytes_model_kind="not counted: NumPy collision temporaries",
        field_storage_bytes=9*n*n*8))
    return rows
