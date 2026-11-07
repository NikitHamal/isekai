"""Procedural GPU-style shader baker (numpy). Produces tileable albedo / normal / metal-rough / emissive maps."""
import numpy as np, io
from PIL import Image

def _lat(n, seed): return np.random.RandomState(seed).rand(n, n)

def vnoise(u, v, f, seed=0):
    """Tileable bilinear value noise; u,v in [0,1)."""
    L = _lat(f, seed); x = u * f; y = v * f; x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
    fx = x - x0; fy = y - y0; fx = fx*fx*(3-2*fx); fy = fy*fy*(3-2*fy); x0 %= f; y0 %= f; x1 = (x0+1) % f; y1 = (y0+1) % f
    return (L[y0, x0]*(1-fx) + L[y0, x1]*fx) * (1-fy) + (L[y1, x0]*(1-fx) + L[y1, x1]*fx) * fy

def fbm(u, v, f=4, oct=5, seed=0):
    a, t, n = 1.0, 0, 0
    for o in range(oct): t += a * vnoise(u, v, f * 2**o, seed + o); n += a; a *= .5
    return t / n

def voronoi(u, v, f=6, seed=0):
    r = np.random.RandomState(seed); pts = r.rand(f, f, 2); gx = np.floor(u*f).astype(int); gy = np.floor(v*f).astype(int)
    d1 = np.full(u.shape, 9.); d2 = np.full(u.shape, 9.)
    for oy in (-1, 0, 1):
        for ox in (-1, 0, 1):
            cx = (gx+ox) % f; cy = (gy+oy) % f; px = gx+ox+pts[cy, cx, 0]; py = gy+oy+pts[cy, cx, 1]
            d = np.hypot(u*f-px, v*f-py); m = d < d1; d2 = np.where(m, d1, np.minimum(d2, d)); d1 = np.minimum(d1, d)
    return d1, d2 - d1  # distance to cell, edge distance

def _mix(a, b, t): return np.asarray(a)[None, None] * (1 - t[..., None]) + np.asarray(b)[None, None] * t[..., None]

def shade(m, n):
    """Return dict(h, albedo, rough, metal, emis) arrays for Material m at n x n."""
    g = (np.arange(n) + .5) / n; u, v = np.meshgrid(g, g); s = max(2, int(m.scale)); c1, c2 = m.color, m.color2
    k = m.shader; E = np.zeros((n, n, 3)); R = np.full((n, n), m.rough); M = np.full((n, n), m.metal)
    if k == "voronoi_stone":
        d, e = voronoi(u, v, s, m.seed); nz = fbm(u, v, 8, 5, m.seed); h = np.clip(e * 3, 0, 1) * .7 + nz * .3
        A = _mix(c1, c2, nz * .8 + d * .3) * (0.55 + 0.45 * np.clip(e * 4, 0, 1))[..., None]
    elif k == "wood_grain":
        w = fbm(u * 1.0, v, 3, 4, m.seed) * 6; ring = np.sin((u * s + w) * 2*np.pi) * .5 + .5; fib = fbm(u * 4, v * 40 % 1.0, 16, 3, m.seed + 7)
        h = ring * .35 + fib * .65; A = _mix(c1, c2, ring * .7 + fib * .3)
    elif k == "hammered_metal":
        d, e = voronoi(u, v, s * 2, m.seed); dent = np.clip(1 - d * 1.5, 0, 1) ** 2; nz = fbm(u, v, 16, 3, m.seed); h = dent * .6 + nz * .4
        A = _mix(c1, c2, nz * .6 + dent * .4); R = np.clip(m.rough + (nz - .5) * .3, .05, 1)
    elif k == "woven_cloth":
        wu = (np.sin(u * s * 2*np.pi * 4) * .5 + .5); wv = (np.sin(v * s * 2*np.pi * 4) * .5 + .5); chk = ((np.floor(u * s * 4) + np.floor(v * s * 4)) % 2)
        h = np.where(chk > 0, wu, wv) * .8 + fbm(u, v, 32, 2, m.seed) * .2; A = _mix(c1, c2, h * .6 + fbm(u, v, 6, 4, m.seed) * .4)
    elif k == "runic_glow":
        d, e = voronoi(u, v, s, m.seed); nz = fbm(u, v, 6, 4, m.seed); line = np.clip(1 - e * 9, 0, 1) * (nz > .42)
        h = nz * .6 + (1 - line) * .4; A = _mix(c1, c2, nz); E = line[..., None] * np.asarray(m.emissive)[None, None] * 1.0
    else:  # fbm_noise
        nz = fbm(u, v, s, 5, m.seed); h = nz; A = _mix(c1, c2, nz)
    if k != "runic_glow" and any(m.emissive):
        E = np.broadcast_to(np.asarray(m.emissive)[None, None] * (0.75 + 0.25 * fbm(u, v, 4, 3, m.seed)[..., None]), (n, n, 3)).copy()
    return dict(h=h, albedo=np.clip(A, 0, 1), rough=R, metal=M, emis=np.clip(E, 0, 1))

def normal_map(h, strength=2.0):
    """Tangent-space normal from Sobel derivative of the height field (tileable wrap)."""
    kx = (np.roll(h, -1, 1) * 2 + np.roll(np.roll(h, -1, 1), -1, 0) + np.roll(np.roll(h, -1, 1), 1, 0)) - (np.roll(h, 1, 1) * 2 + np.roll(np.roll(h, 1, 1), -1, 0) + np.roll(np.roll(h, 1, 1), 1, 0))
    ky = (np.roll(h, -1, 0) * 2 + np.roll(np.roll(h, -1, 0), -1, 1) + np.roll(np.roll(h, -1, 0), 1, 1)) - (np.roll(h, 1, 0) * 2 + np.roll(np.roll(h, 1, 0), -1, 1) + np.roll(np.roll(h, 1, 0), 1, 1))
    nx = -kx * strength * .25; ny = -ky * strength * .25; nz = np.ones_like(h)
    l = np.sqrt(nx*nx + ny*ny + nz*nz); return np.stack([nx / l, ny / l, nz / l], -1) * .5 + .5

def _png(a):
    b = io.BytesIO(); Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(b, "PNG", optimize=True); return b.getvalue()

def bake(m, n=512):
    """-> dict of PNG bytes: albedo, normal, mr (glTF: G=rough, B=metal), emissive (or None)."""
    r = shade(m, n); mr = np.stack([np.ones((n, n)), r["rough"], r["metal"]], -1)
    return dict(albedo=_png(r["albedo"]), normal=_png(normal_map(r["h"], m.bump)), mr=_png(mr),
                emissive=_png(r["emis"]) if r["emis"].max() > 0.01 else None)
