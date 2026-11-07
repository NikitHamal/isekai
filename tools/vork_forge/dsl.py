"""vork_forge DSL: compact declarative 3D mesh combinators (numpy). Part 1: core + basic primitives."""
import numpy as np
from dataclasses import dataclass, field

def _rot(r):
    rx, ry, rz = [np.radians(a) for a in r]
    cx, sx, cy, sy, cz, sz = np.cos(rx), np.sin(rx), np.cos(ry), np.sin(ry), np.cos(rz), np.sin(rz)
    X = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); Y = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]); Z = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    return Z @ Y @ X

class Mesh:
    def __init__(s, V, F, UV=None):
        s.V = np.asarray(V, float).reshape(-1, 3); s.F = np.asarray(F, np.int64).reshape(-1, 3)
        s.UV = np.zeros((len(s.V), 2)) if UV is None else np.asarray(UV, float).reshape(-1, 2)
    @property
    def tris(s): return len(s.F)
    def tf(s, pos=(0,0,0), rot=(0,0,0), scale=(1,1,1)):
        sc = np.broadcast_to(np.asarray(scale, float), (3,))
        return Mesh((s.V * sc) @ _rot(rot).T + np.asarray(pos, float), s.F.copy(), s.UV.copy())
    def normals(s):
        v = s.V; f = s.F; fn = np.cross(v[f[:,1]]-v[f[:,0]], v[f[:,2]]-v[f[:,0]])
        n = np.zeros_like(v)
        for i in range(3): np.add.at(n, f[:,i], fn)
        l = np.linalg.norm(n, axis=1, keepdims=True); l[l < 1e-12] = 1
        return n / l
    def __add__(s, o): return merge([s, o])

def merge(meshes):
    meshes = [m for m in meshes if m is not None and len(m.F)]
    off = np.cumsum([0] + [len(m.V) for m in meshes[:-1]])
    return Mesh(np.vstack([m.V for m in meshes]), np.vstack([m.F + o for m, o in zip(meshes, off)]), np.vstack([m.UV for m in meshes]))

@dataclass
class Material:
    name: str; shader: str = "fbm_noise"; color: tuple = (0.6, 0.6, 0.6); color2: tuple = (0.3, 0.3, 0.3)
    rough: float = 0.7; metal: float = 0.0; emissive: tuple = (0, 0, 0); scale: float = 6.0; bump: float = 2.0
    alpha: float = 1.0; seed: int = 1

@dataclass
class Node:
    name: str; mesh: Mesh = None; material: Material = None; children: list = field(default_factory=list)
    pos: tuple = (0,0,0); rot: tuple = (0,0,0); scale: tuple = (1,1,1); part_id: int = 0; pivot: tuple = (0,0,0)

def node(name, mesh=None, material=None, children=(), pos=(0,0,0), rot=(0,0,0), scale=(1,1,1), part_id=0, pivot=(0,0,0)):
    return Node(name, mesh, material, list(children), pos, rot, scale, part_id, pivot)

def grid(P, uscale=1.0, vscale=1.0, closed_u=True, cap=False, flip=False):
    """P: (rows, cols, 3) -> quad-grid mesh. Wraps columns when closed_u."""
    r, c, _ = P.shape; V = P.reshape(-1, 3)
    u = np.linspace(0, uscale, c); v = np.linspace(0, vscale, r)
    UV = np.stack(np.meshgrid(u, v), -1).reshape(-1, 2)
    cc = c - 1 if closed_u else c - 1
    i, j = np.meshgrid(np.arange(r-1), np.arange(cc), indexing="ij"); a = (i*c+j).ravel(); b = (i*c+(j+1)).ravel()
    d = ((i+1)*c+j).ravel(); e = ((i+1)*c+(j+1)).ravel()
    F = np.vstack([np.stack([a, d, b], 1), np.stack([b, d, e], 1)])
    m = Mesh(V, F[:, [0, 2, 1]] if flip else F, UV)
    if cap:
        for row, o in ((0, P[0].mean(0) - P[1].mean(0)), (r-1, P[-1].mean(0) - P[-2].mean(0))):
            ring = P[row, :-1] if closed_u else P[row]; ctr = ring.mean(0); k = len(ring); ids = np.arange(k)
            fc = np.stack([np.zeros(k, int), ids + 1, (ids + 1) % k + 1], 1)
            nrm = np.cross(ring - ctr, np.roll(ring, -1, 0) - ctr).sum(0)
            if nrm @ o < 0: fc = fc[:, [0, 2, 1]]
            m = merge([m, Mesh(np.vstack([ctr, ring]), fc, np.zeros((k+1, 2)) + .5)])
    return m

def box(size=(1,1,1), pos=(0,0,0), rot=(0,0,0), seg=1):
    """Subdivided box (seg per face edge) with per-face UVs."""
    faces = []
    for ax in range(3):
        for sg in (-1, 1):
            a, b = (ax+1) % 3, (ax+2) % 3
            g = np.linspace(-.5, .5, seg+1); A, B = np.meshgrid(g, g); P = np.zeros((seg+1, seg+1, 3))
            P[..., ax] = .5*sg; P[..., a] = A; P[..., b] = B
            m = grid(P, closed_u=False)
            if sg > 0: m.F = m.F[:, [0, 2, 1]]
            faces.append(m)
    return merge(faces).tf(pos, rot, size)

def sphere(r=1.0, pos=(0,0,0), scale=(1,1,1), rings=24, sides=32, rot=(0,0,0)):
    th = np.linspace(np.pi, 0, rings+1)[:, None]; ph = np.linspace(0, 2*np.pi, sides+1)[None]
    P = np.stack([r*np.sin(th)*np.cos(ph), r*np.cos(th)+0*ph, r*np.sin(th)*np.sin(ph)], -1)
    return grid(P).tf(pos, rot, scale)

def cylinder(r=0.5, h=1.0, pos=(0,0,0), r2=None, sides=32, rings=1, rot=(0,0,0), cap=True):
    r2 = r if r2 is None else r2; y = np.linspace(-h/2, h/2, rings+1)[:, None]; ph = np.linspace(0, 2*np.pi, sides+1)[None]
    rr = r + (r2 - r) * (y + h/2) / h
    return grid(np.stack([rr*np.cos(ph), y+0*ph, rr*np.sin(ph)], -1), cap=cap).tf(pos, rot)

def torus(R=1.0, r=0.2, pos=(0,0,0), rot=(0,0,0), seg=48, sides=16, scale=(1,1,1)):
    u = np.linspace(0, 2*np.pi, seg+1)[:, None]; v = np.linspace(0, 2*np.pi, sides+1)[None]
    P = np.stack([(R + r*np.cos(v))*np.cos(u), r*np.sin(v)+0*u, (R + r*np.cos(v))*np.sin(u)], -1)
    return grid(P, flip=True).tf(pos, rot, scale)

def lathe(profile_2d, segments=48, bevel=True, pos=(0,0,0), rot=(0,0,0), scale=(1,1,1)):
    """profile_2d: [(radius, y), ...]; spins about Y. Bevel = Chaikin-rounded profile."""
    p = np.asarray(profile_2d, float)
    if bevel and len(p) > 2:
        for _ in range(2):
            q = [p[0]]
            for a, b in zip(p[:-1], p[1:]): q += [.75*a + .25*b, .25*a + .75*b]
            p = np.vstack(q + [p[-1]])
    ph = np.linspace(0, 2*np.pi, segments+1)[None]; r = p[:, :1]; y = p[:, 1:]
    return grid(np.stack([r*np.cos(ph), y+0*ph, r*np.sin(ph)], -1), uscale=3.0).tf(pos, rot, scale)

# ---------------- Part 2: organic, SDF, masonry, timber, subdivision ----------------
def _hash_noise(P, seed=0, freq=1.0):
    """Cheap smooth value-noise on 3D points (sum of sines, vectorised)."""
    r = np.random.RandomState(seed); k = r.randn(4, 3) * freq; ph = r.rand(4) * 6.28
    return sum(np.sin(P @ k[i] + ph[i]) for i in range(4)) / 4

def catmull(points, n=48):
    p = np.asarray(points, float)
    if len(p) == 2: return np.linspace(p[0], p[1], n)
    q = np.vstack([2*p[0]-p[1], p, 2*p[-1]-p[-2]]); out = []; seg = len(p) - 1
    t = np.linspace(0, seg, n)
    for x in t:
        i = min(int(x), seg-1); u = x - i; a, b, c, d = q[i], q[i+1], q[i+2], q[i+3]
        out.append(.5*((2*b) + (-a+c)*u + (2*a-5*b+4*c-d)*u*u + (-a+3*b-3*c+d)*u**3))
    return np.array(out)

def spline_tube(points, radii, twist=0.0, rings=48, sides=24, bark_disp=0.04, seed=0, cap=True, flat=1.0):
    """Sweep a (bark-displaced) tube along a Catmull-Rom spline; radii interpolated along length."""
    C = catmull(points, rings); T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9
    ref = np.array([0, 1, 0.]) if abs(T[0, 1]) < .95 else np.array([1, 0, 0.]); N0 = np.cross(T[0], ref); N0 /= np.linalg.norm(N0)
    Ns = []
    for t in T:  # parallel transport
        N0 = N0 - t * (N0 @ t); N0 /= np.linalg.norm(N0) + 1e-9; Ns.append(N0.copy())
    Ns = np.array(Ns); Bs = np.cross(T, Ns)
    rad = np.interp(np.linspace(0, 1, rings), np.linspace(0, 1, len(radii)), radii)[:, None]
    ph = np.linspace(0, 2*np.pi, sides+1)[None] + twist * np.linspace(0, 1, rings)[:, None]
    dirs = np.cos(ph)[..., None] * Ns[:, None] + np.sin(ph)[..., None] * flat * Bs[:, None]
    P = C[:, None] + dirs * rad[..., None]
    if bark_disp: P = P + dirs * (_hash_noise(P.reshape(-1, 3), seed, 9.0).reshape(rings, sides+1, 1) * bark_disp * rad[..., None] * 4)
    P[:, -1] = P[:, 0]
    return grid(P, uscale=2.0, vscale=max(1.0, np.linalg.norm(np.diff(C, axis=0), axis=1).sum()), cap=cap, flip=True)

def _smin(a, b, k): h = np.clip(.5 + .5*(b-a)/k, 0, 1); return b*(1-h) + a*h - k*h*(1-h)

def sdf_sculpt(primitives, resolution=64, smooth_k=0.15, pad=0.3):
    """primitives: ('sphere',c,r) | ('ellipsoid',c,(rx,ry,rz)) | ('capsule',a,b,r) [+ 'sub' flag as 4th/5th tuple elt via ('-',prim)].
    Smooth-min blends all; marching cubes -> watertight mesh with triplanar UVs."""
    from skimage.measure import marching_cubes
    pts = []
    for p in primitives:
        q = p[1:] if p[0] != '-' else p[1][1:]
        for e in q:
            if np.ndim(e) == 1 and len(e) == 3: pts.append(np.asarray(e, float))
        rr = [e for e in q if np.ndim(e) == 0]; ee = [e for e in q if np.ndim(e) == 1 and len(e) == 3]
    lo = np.min(pts, 0) - 1.2 - pad; hi = np.max(pts, 0) + 1.2 + pad
    ax = [np.linspace(lo[i], hi[i], resolution) for i in range(3)]
    X, Y, Z = np.meshgrid(*ax, indexing="ij"); G = np.stack([X, Y, Z], -1)
    d = np.full(X.shape, 1e3)
    for p in primitives:
        sub = p[0] == '-'; pr = p[1] if sub else p
        if sub: pr = p[1]
        kind = pr[0]
        if kind == 'sphere': di = np.linalg.norm(G - np.asarray(pr[1]), axis=-1) - pr[2]
        elif kind == 'ellipsoid':
            c = np.asarray(pr[1]); r = np.asarray(pr[2], float); k0 = np.linalg.norm((G-c)/r, axis=-1); di = (k0 - 1) * r.min()
        else:
            a = np.asarray(pr[1], float); b = np.asarray(pr[2], float); ba = b - a; t = np.clip(((G-a) @ ba) / (ba @ ba), 0, 1)
            di = np.linalg.norm(G - (a + t[..., None]*ba), axis=-1) - pr[3]
        d = np.maximum(d, -di) if sub else _smin(d, di, smooth_k)
    sp = [(ax[i][1]-ax[i][0]) for i in range(3)]
    v, f, n, _ = marching_cubes(d, 0.0, spacing=sp); v = v + lo
    n = np.abs(n) / (np.abs(n).sum(1, keepdims=True) + 1e-9); uv = v[:, [0, 2]] * n[:, 1:2] + v[:, [0, 1]] * n[:, 2:3] + v[:, [2, 1]] * n[:, 0:1]
    return Mesh(v, f, uv * 0.5)

def subdivide(mesh, levels=2, smooth=0.5):
    """1->4 midpoint split followed by Laplacian relaxation (Loop-like smoothing)."""
    m = mesh
    for _ in range(levels):
        V, F, UV = m.V, m.F, m.UV; cache = {}; nv = list(V); nu = list(UV)
        def mid(a, b):
            k = (min(a, b), max(a, b))
            if k not in cache: cache[k] = len(nv); nv.append((V[a] + V[b]) / 2); nu.append((UV[a] + UV[b]) / 2)
            return cache[k]
        NF = []
        for a, b, c in F:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a); NF += [(a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)]
        W = np.array(nv); NF = np.array(NF)
        if smooth:
            acc = np.zeros_like(W); cnt = np.zeros(len(W))
            for i, j in ((0, 1), (1, 2), (2, 0)):
                np.add.at(acc, NF[:, i], W[NF[:, j]]); np.add.at(cnt, NF[:, i], 1)
            # weld-safe: only blend toward neighbour mean lightly to keep silhouette
            W = W * (1 - smooth * .5) + (acc / cnt[:, None]) * smooth * .5
        m = Mesh(W, NF, np.array(nu))
    return m

def arch_masonry(span=3.0, height=3.5, depth=1.0, stones=18, moss_factor=0.5, seed=3):
    """Beveled voussoir stone arch on two jamb pillars. Returns Mesh."""
    r = np.random.RandomState(seed); parts = []; R = span / 2; t = 0.45
    for side in (-1, 1):
        for k in range(int(height / .5)):
            parts.append(box((t + r.rand()*.1, .5, depth*(.95 + r.rand()*.1)), (side*(R + t/2), .25 + k*.5, 0), (0, r.randn()*2, 0), seg=3))
    for i in range(stones):
        a0, a1 = np.pi * i / stones, np.pi * (i+1) / stones; am = (a0 + a1) / 2; w = np.pi * (R + t/2) / stones
        parts.append(box((t + r.rand()*.08, w*1.02, depth), (np.cos(np.pi-am)*(R+t/2), height + np.sin(am)*(R+t/2) - .2, 0), (0, 0, np.degrees(np.pi-am) - 90 + 90), seg=3))
    return merge(parts)

def timber_frame(beams, rope_knots=True, beam_w=0.22, seed=5):
    """beams: [(a, b)] 3D endpoints -> squared-ish tapered beams with optional rope-wrapped joints."""
    r = np.random.RandomState(seed); parts = []
    for a, b in beams:
        a = np.asarray(a, float); b = np.asarray(b, float)
        parts.append(spline_tube([a, (a+b)/2 + r.randn(3)*.03, b], [beam_w*.55, beam_w*.6, beam_w*.55], rings=10, sides=8, bark_disp=.08, seed=r.randint(99)))
        if rope_knots:
            for e in (a + (b-a)*.12, b + (a-b)*.12):
                parts.append(torus(beam_w*.6, .03, e, rot=tuple(np.degrees(np.arctan2(*(b-a)[[0, 1]][::-1]) * np.array([0, 0, 1])) + [90, 0, 0] if False else (0, 0, 0)), seg=16, sides=6))
    return merge(parts)
