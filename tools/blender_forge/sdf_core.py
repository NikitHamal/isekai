#!/usr/bin/env python3
"""SDF anatomy sculpting core (numpy).  Characters are modelled as smooth-union signed-distance fields of tapered capsules and ellipsoid
muscle volumes (deltoids, pecs, biceps, calves, jaw, brow ridge ...), meshed with marching cubes, snapped onto the true isosurface with a
Newton step, and given analytic smooth normals.  Fitted clothing / armour are *offset shells* of the same field.  Blender space: Z up,
character front = -Y, character-left = +X (glTF export maps to Y-up / +Z forward)."""
import numpy as np
from skimage.measure import marching_cubes

def A(*a): return np.array(a[0] if len(a) == 1 else a, float)

def smin(a, b, k):
    h = np.clip(.5 + .5 * (b - a) / k, 0, 1); return b * (1 - h) + a * h - k * h * (1 - h)

def cap(a, b, ra, rb=None):
    """tapered capsule (round cone) from a to b."""
    a, b = A(a), A(b); rb = ra if rb is None else rb; ba = b - a; bb = float(ba @ ba) + 1e-12
    def f(P):
        pa = P - a; t = np.clip(pa @ ba / bb, 0, 1); q = pa - t[:, None] * ba
        return np.sqrt((q * q).sum(1)) - (ra + (rb - ra) * t)
    return f

def ell(c, r, rot=None):
    """ellipsoid with semi-axes r (optionally rotated by 3x3 `rot`, local->world)."""
    c, r = A(c), A(r)
    def f(P):
        q = P - c
        if rot is not None: q = q @ rot
        k0 = np.sqrt(((q / r) ** 2).sum(1)) + 1e-9; k1 = np.sqrt(((q / (r * r)) ** 2).sum(1)) + 1e-9
        return k0 * (k0 - 1) / k1
    return f

def ellz(c, r, dirv, up=(1, 0, 0)):
    """ellipsoid whose local Z axis points along dirv (muscle belly along a limb); local X ~ `up` projected (default world X), Y = front/back."""
    z = A(dirv); z = z / np.linalg.norm(z); x = A(up) - (A(up) @ z) * z
    if np.linalg.norm(x) < 1e-3: x = A(0, 1, 0) - z[1] * z
    x /= np.linalg.norm(x); y = np.cross(z, x); return ell(c, r, np.stack([x, y, z], 1))

def rbox(c, h, rad=.01):
    c, h = A(c), A(h)
    def f(P):
        q = np.abs(P - c) - h + rad; return np.sqrt((np.maximum(q, 0) ** 2).sum(1)) + np.minimum(q.max(1), 0) - rad
    return f

def U(fs, k=.03):
    """smooth union of SDF callables."""
    def f(P):
        d = fs[0](P)
        for g in fs[1:]: d = smin(d, g(P), k)
        return d
    return f

def sub(f, g, k=.01):
    return lambda P: -smin(-f(P), g(P), k)

def inter(f, g): return lambda P: np.maximum(f(P), g(P))
def off(f, d): return lambda P: f(P) - d
def mirror(f): return lambda P: f(P * np.array([-1., 1, 1]))
def sym(f, k=.03): g = mirror(f); return U([f, g], k)

def add_noise(f, fn, amp):
    """displace the surface by amp * fn(P) (fn in -1..1) -- real geometric surface detail (scales, wrinkles, cracks)."""
    return lambda P: f(P) - amp * fn(P)

def extract(f, lo, hi, h, keep=None, push=0.0):
    """marching cubes over [lo,hi] with voxel h; returns verts (n,3), tris (m,3) outward wound, smooth normals (n,3)."""
    lo, hi = A(lo), A(hi); n = np.ceil((hi - lo) / h).astype(int) + 1
    ax = [lo[i] + np.arange(n[i]) * h for i in range(3)]
    X = np.stack(np.meshgrid(*ax, indexing="ij"), -1).reshape(-1, 3)
    vol = f(X).reshape(n).astype(np.float32)
    if vol.min() > 0 or vol.max() < 0: return np.zeros((0, 3), np.float32), np.zeros((0, 3), np.int64), np.zeros((0, 3), np.float32)
    v, fc, _, _ = marching_cubes(vol, 0.0, spacing=(h, h, h)); v = v + lo; e = h * .3
    def nrm(p):
        g = np.stack([f(p + e * d) - f(p - e * d) for d in np.eye(3)], 1); return g / (np.linalg.norm(g, axis=1, keepdims=True) + 1e-9)
    nr = nrm(v); v = v - f(v)[:, None] * nr; nr = nrm(v)
    a, b, c = v[fc[:, 0]], v[fc[:, 1]], v[fc[:, 2]]; flip = (np.cross(b - a, c - a) * nr[fc].mean(1)).sum(1) < 0; fc[flip] = fc[flip][:, ::-1]
    if keep is not None:
        fc = fc[keep(v[fc].mean(1))]
        used = np.unique(fc); rm = -np.ones(len(v), int); rm[used] = np.arange(len(used)); v, nr, fc = v[used], nr[used], rm[fc]
    return (v + nr * push).astype(np.float32), fc.astype(np.int64), nr.astype(np.float32)

def seg_dist(P, a, b):
    a, b = A(a), A(b); ba = b - a; t = np.clip((P - a) @ ba / (float(ba @ ba) + 1e-12), 0, 1)
    return np.linalg.norm(P - a - t[:, None] * ba, axis=1)

def weights(P, segs, tau=.03):
    """segs: {partId: [(a, b), ...]} bone segments -> (j0, j1, blend) top-2 soft part influences per vertex (engine part-blend skinning)."""
    ids = list(segs); D = np.stack([np.min([seg_dist(P, a, b) for a, b in segs[i]], 0) for i in ids], 1)
    W = np.exp(-(D - D.min(1, keepdims=True)) / tau); W /= W.sum(1, keepdims=True); ix = np.argsort(-W, 1)[:, :2]; r = np.arange(len(P))
    w0, w1 = W[r, ix[:, 0]], W[r, ix[:, 1]]; wb = np.where(w1 > .03, w1 / (w0 + w1), 0.)
    return np.array(ids)[ix[:, 0]], np.array(ids)[ix[:, 1]], np.minimum(wb, .99)

def merge(parts):
    """concatenate (V,F,N) tuples."""
    Vs, Fs, Ns, o = [], [], [], 0
    for V, F, N in parts:
        Vs.append(V); Fs.append(F + o); Ns.append(N); o += len(V)
    return np.vstack(Vs), np.vstack(Fs), np.vstack(Ns)
