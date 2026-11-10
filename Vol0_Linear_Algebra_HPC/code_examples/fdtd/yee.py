"""Periodic 3D staggered Yee update in normalized vacuum; all six component arrays."""
from time import perf_counter
import itertools
import numpy as np
from common import timed, record


def diff(a, axis, h, forward=True):
    if forward:
        return (np.roll(a,-1,axis=axis)-a)/h
    return (a-np.roll(a,1,axis=axis))/h


def curl(field, h, forward=True):
    x,y,z = field
    return np.array([diff(z,1,h,forward)-diff(y,2,h,forward),
                     diff(x,2,h,forward)-diff(z,0,h,forward),
                     diff(y,0,h,forward)-diff(x,1,h,forward)])


def divergence(field,h,forward=True):
    return sum(diff(field[j],j,h,forward) for j in range(3))


def step(e,b,dt,h):
    new_b = b-dt*curl(e,h,True)
    new_e = e+dt*curl(new_b,h,False)
    return new_e,new_b


def modified_energy(e,b,dt,h):
    next_b = b-dt*curl(e,h,True)
    return float(.5*h**3*(np.sum(e*e)+np.sum(b*next_b)))


def incidence_check():
    vertices = list(itertools.product((0,1),repeat=3))
    index = {v:i for i,v in enumerate(vertices)}
    edges = []
    for v in vertices:
        for axis in range(3):
            if v[axis] == 0:
                w = list(v); w[axis] = 1
                edges.append((v,tuple(w)))
    lookup = {edge:j for j,edge in enumerate(edges)}
    g = np.zeros((12,8),dtype=int)
    for i,(a,b) in enumerate(edges):
        g[i,index[a]]=-1; g[i,index[b]]=1
    faces = [
        [(0,0,0),(0,1,0),(1,1,0),(1,0,0)],
        [(0,0,1),(1,0,1),(1,1,1),(0,1,1)],
        [(0,0,0),(0,0,1),(0,1,1),(0,1,0)],
        [(1,0,0),(1,1,0),(1,1,1),(1,0,1)],
        [(0,0,0),(1,0,0),(1,0,1),(0,0,1)],
        [(0,1,0),(0,1,1),(1,1,1),(1,1,0)]]
    c = np.zeros((6,12),dtype=int)
    for f,loop in enumerate(faces):
        for a,b in zip(loop,loop[1:]+loop[:1]):
            if (a,b) in lookup:
                c[f,lookup[(a,b)]]=1
            else:
                c[f,lookup[(b,a)]]=-1
    d = np.ones((1,6),dtype=int)
    assert not np.any(c@g) and not np.any(d@c)
    return {"G_shape":list(g.shape),"C_shape":list(c.shape),"D_shape":list(d.shape),
            "CG_max":int(abs(c@g).max()),"DC_max":int(abs(d@c).max())}


def constraint_check():
    n=7; h=1/n; dt=.3*h
    rng=np.random.default_rng(42)
    e=curl(rng.normal(size=(3,n,n,n)),h,False)
    b=curl(rng.normal(size=(3,n,n,n)),h,True)
    divb0=divergence(b,h,True); dive0=divergence(e,h,False)
    initial=modified_energy(e,b,dt,h)
    for _ in range(10):
        e,b=step(e,b,dt,h)
    divb=float(np.max(abs(divergence(b,h,True)-divb0)))
    dive=float(np.max(abs(divergence(e,h,False)-dive0)))
    energy=abs(modified_energy(e,b,dt,h)-initial)/initial
    assert divb < 5e-11 and dive < 5e-11 and energy < 1e-12
    return {"random_field_divB_drift":divb,"random_field_divE_drift":dive,
            "modified_energy_relative_drift":energy,**incidence_check()}


def wave(n, final_time=.5):
    h=1/n
    steps=int(np.ceil(final_time/(.45*h)))
    dt=final_time/steps
    shape=(3,n,n,n)
    e=np.zeros(shape); b=np.zeros(shape)
    x=np.arange(n)*h
    e[1]=np.sin(2*np.pi*x)[:,None,None]
    b[2]=np.sin(2*np.pi*(x+.5*h+.5*dt))[:,None,None]
    initial=modified_energy(e,b,dt,h)
    start=perf_counter()
    for _ in range(steps):
        e,b=step(e,b,dt,h)
    elapsed=perf_counter()-start
    exact_e=np.sin(2*np.pi*(x-final_time))[:,None,None]
    exact_b=np.sin(2*np.pi*(x+.5*h-(final_time-.5*dt)))[:,None,None]
    error_e=float(np.sqrt(np.mean((e[1]-exact_e)**2)))
    error_b=float(np.sqrt(np.mean((b[2]-exact_b)**2)))
    divb=float(np.max(abs(divergence(b,h,True))))
    dive=float(np.max(abs(divergence(e,h,False))))
    edrift=abs(modified_energy(e,b,dt,h)-initial)/initial
    assert edrift < 1e-12 and divb < 1e-12 and dive < 1e-12
    return record("yee_wave",{"seconds":elapsed,"repeats":1,"warmup_calls":0},
        {"n":n,"dofs":6*n**3,"h":h,"dt":dt,"steps":steps,"T":final_time,
         "courant":dt/h,"boundary":"periodic","epsilon":1,"mu":1,"order":2,
         "b_initial_time":-.5*dt},42*n**3*steps,144*n**3*steps,
        bytes_model_kind="two_phase_ideal_reuse_not_numpy_temporaries",
        field_storage_bytes=6*n**3*8,error_e_L2=error_e,error_b_L2=error_b,
        divB_max=divb,divE_max=dive,modified_energy_relative_drift=edrift,
        numerical_omega=float(2/dt*np.arcsin(dt/h*np.sin(np.pi*h))),
        kernel_scope="numpy full 3D periodic advance; allocations included; diagnostics excluded")


def run():
    rows=[wave(n) for n in (12,24)]
    ratio=rows[0]["error_e_L2"]/rows[1]["error_e_L2"]
    assert 3.3 < ratio < 4.7, ratio
    rng=np.random.default_rng(22); n=32; h=1/n
    e=rng.normal(size=(3,n,n,n)); b=rng.normal(size=e.shape)
    _,timing=timed(lambda:step(e,b,.4*h,h))
    rows.append(record("yee_single_step",timing,{"n":n,"dofs":6*n**3,"dt":.4*h,
        "steps":1,"order":2},42*n**3,144*n**3,
        bytes_model_kind="two_phase_ideal_reuse; Python temporaries excluded",
        alternative_bytes_per_cell={"semantic":288,"two_phase_ideal":144,"resident_lower_bound":96}))
    return rows
