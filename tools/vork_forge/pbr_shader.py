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

def _hv(a, seed):
    """Deterministic per-cell hash in [0,1) for integer cell ids."""
    x = np.sin(a.astype(float) * 12.9898 + seed * 78.233) * 43758.5453; return x - np.floor(x)

def _courses(u, v, rows, cols, seed, stagger=True, rowjit=0.0):
    """Tileable running-bond layout. Returns (cell_hash, edge_dist_in_uv, fu, fv)."""
    r = v * rows; ri = np.floor(r).astype(int); fv = r - ri; ri %= rows
    sh = np.random.RandomState(seed).rand(rows) if stagger else np.zeros(rows)
    c = u * cols + sh[ri]; ci = np.floor(c).astype(int); fu = c - ci; ci %= cols
    ed = np.minimum(np.minimum(fu, 1 - fu) / cols, np.minimum(fv, 1 - fv) / rows)
    return _hv(ci * 31 + ri * 57, seed), ed, fu, fv

def _shade_ext(m, n):
    g = (np.arange(n) + .5) / n; u, v = np.meshgrid(g, g); s = max(2, int(m.scale)); c1, c2 = m.color, m.color2; k = m.shader
    E = np.zeros((n, n, 3)); R = np.full((n, n), m.rough); M = np.full((n, n), m.metal)
    if k in ("cut_stone", "stone_face"):       # weathered ashlar masonry: staggered courses, mortar grooves, chipped bevels, grime + lichen streaks
        hsh, ed, fu, fv = _courses(u, v, s, max(2, s // 2 + 1), m.seed); gap = .0045 if k == "cut_stone" else -1.0; groove = np.clip((ed - gap) / .006, 0, 1)
        nz = fbm(u, v, 8, 5, m.seed); fine = fbm(u, v, 64, 3, m.seed + 3); chip = np.clip(1 - ed / .02, 0, 1) * (fbm(u, v, 32, 3, m.seed + 9) > .5)
        h = groove * (.55 + .25 * nz + .2 * fine) - chip * .25; A = _mix(c1, c2, np.clip(hsh * .7 + nz * .5 - .15, 0, 1))
        A = A * (.8 + .35 * fine)[..., None]; streak = np.clip(fbm(u * 3 % 1, v, 6, 4, m.seed + 5) * 1.6 - .75, 0, 1) * (1 - v) ** .7
        A = A * (1 - .45 * streak)[..., None] + np.asarray((.12, .2, .06))[None, None] * (.35 * streak)[..., None]
        mort = np.asarray((.3, .28, .25))[None, None] * (.7 + .5 * fine[..., None]); A = A * groove[..., None] + mort * (1 - groove[..., None]); R = np.clip(m.rough + (1 - groove) * .05 - .1 * chip, .3, 1)
    elif k == "plank_timber":  # rough oak planks: vertical boards, dark gaps, grain, knots, nail heads, weathering
        pl = np.floor(u * s); fu = u * s - pl; hs = _hv(pl, m.seed); gapd = np.minimum(fu, 1 - fu) / s; gr = np.clip((gapd - .0025) / .004, 0, 1)
        warp = fbm(u, v, 3, 4, m.seed) * 5; grain = np.sin((fu * 14 + warp + hs[..., None][..., 0] * 9) * 2 * np.pi) * .5 + .5; fib = fbm(u * 2, (v * 48) % 1.0, 24, 3, m.seed + 7)
        kn = voronoi(u, v, 5, m.seed + 2)[0]; knot = np.clip(1 - kn * 7, 0, 1) ** 2 * (hs > .55)
        h = (grain * .3 + fib * .5 + knot * .3) * gr; A = _mix(c1, c2, np.clip(grain * .45 + fib * .45 + hs * .25 + knot * .5 - .1, 0, 1)) * (.55 + .45 * gr)[..., None]
        weather = fbm(u, v, 5, 4, m.seed + 4); A = A * (.8 + .3 * weather)[..., None] + (.06 * (weather > .62))[..., None]; R = np.clip(m.rough + (fib - .5) * .2, .3, 1)
    elif k == "damascus":      # forged pattern-welded steel: wavy layered bands, hammer scale, edge wear scratches
        w = fbm(u, v, 4, 4, m.seed) * 3.0 + fbm(u, v, 8, 3, m.seed + 1); bands = np.sin((v * s * 3 + w * 3.2) * 2 * np.pi) * .5 + .5; bands2 = np.sin((v * s * 7 + w * 6) * 2 * np.pi) * .5 + .5
        scr = fbm((u * 2) % 1, v, 4, 3, m.seed + 6); scratch = np.clip((fbm(u * 1, (v * 96) % 1.0, 48, 2, m.seed + 8) - .62) * 5, 0, 1)
        h = bands * .35 + bands2 * .15 + scratch * -.12 + .4; A = _mix(c1, c2, np.clip(bands * .65 + bands2 * .2 + scr * .15, 0, 1)) * (1 - .25 * scratch)[..., None]
        R = np.clip(m.rough + (bands - .5) * .2 + scratch * .25, .1, 1); M = np.clip(m.metal - scratch * .25 - (scr > .72) * .35, 0, 1)
    elif k == "stitched_leather":  # pebbled grain, dark creases, stitch rows
        d, e = voronoi(u, v, s * 3, m.seed); peb = np.clip(1 - d * 1.3, 0, 1); crease = np.clip(1 - e * 10, 0, 1); nz = fbm(u, v, 6, 4, m.seed); st = (np.sin(v * s * 2 * 2 * np.pi * 6) > 0) * (np.abs((u * s * 2) % 1.0 - .5) < .06)
        h = peb * .5 + nz * .3 - crease * .35 + st * .25; A = _mix(c1, c2, np.clip(nz * .7 + peb * .3, 0, 1)) * (1 - .35 * crease)[..., None]; A = A * (1 - st[..., None] * .4) + st[..., None] * np.asarray((.75, .65, .45))[None, None] * .5
    elif k == "royal_cloth":   # fine twill weave, heraldic gold border stripes
        tw = np.sin((u * s * 8 + v * s * 8) * 2 * np.pi) * .5 + .5; wv = (np.floor(u * s * 16) + np.floor(v * s * 16)) % 2; h = tw * .6 + wv * .25 + fbm(u, v, 32, 2, m.seed) * .15
        A = _mix(c1, c2, np.clip(h * .4 + fbm(u, v, 5, 4, m.seed) * .3, 0, 1)); stripe = (np.abs(v - .5) < .06) | (np.abs(v - .1) < .015) | (np.abs(v - .9) < .015); A = np.where(stripe[..., None], np.asarray((.85, .66, .22))[None, None] * (.8 + .3 * tw[..., None]), A)
    elif k == "scales":        # overlapping reptilian / armour scales
        d, e = voronoi(u, v, s, m.seed); nz = fbm(u, v, 8, 4, m.seed); plate = np.clip(e * 6, 0, 1); h = plate * .8 + (1 - d) * .2 + nz * .1
        A = _mix(c1, c2, np.clip(nz * .6 + d * .5, 0, 1)) * (.45 + .55 * plate)[..., None]; R = np.clip(m.rough - plate * .15, .1, 1)
    elif k == "slate_shingle": # overlapping slate roof tiles, per-tile tint and moss
        hsh, ed, fu, fv = _courses(u, v, s, max(3, s), m.seed); lip = np.clip(fv * 1.4, 0, 1); gr = np.clip((ed - .002) / .004, 0, 1); nz = fbm(u, v, 12, 4, m.seed)
        h = lip * .6 * gr + nz * .25; A = _mix(c1, c2, np.clip(hsh * .8 + nz * .3, 0, 1)) * (.6 + .4 * lip * gr)[..., None]; A = A + np.asarray((.05, .1, .02))[None, None] * (nz > .7)[..., None] * .8
    elif k == "plaster":       # lime plaster infill with hairline cracks, grime and trowel marks
        nz = fbm(u, v, 5, 5, m.seed); d, e = voronoi(u, v, 5, m.seed); crack = np.clip(1 - e * 28, 0, 1) * (nz > .45); h = nz * .4 - crack * .6 + fbm(u, v, 48, 2, m.seed) * .1
        A = _mix(c1, c2, np.clip(nz * .9, 0, 1)) * (1 - .45 * crack)[..., None] * (1 - .2 * (1 - v) ** 3)[..., None]
    elif k == "cobble":        # mud-and-cobble road
        d, e = voronoi(u, v, s, m.seed); stone = np.clip(e * 7, 0, 1); nz = fbm(u, v, 12, 4, m.seed); h = stone * .8 + nz * .2; A = _mix(c1, c2, np.clip(nz + d * .3, 0, 1)) * (.5 + .5 * stone)[..., None]
    else: return None
    if any(m.emissive): E = np.broadcast_to(np.asarray(m.emissive)[None, None] * (0.75 + 0.25 * fbm(u, v, 4, 3, m.seed)[..., None]), (n, n, 3)).copy()
    return dict(h=h, albedo=np.clip(A, 0, 1), rough=R, metal=M, emis=np.clip(E, 0, 1))

def shade(m, n):
    r = _shade_ext(m, n) if m.shader in ("cut_stone", "stone_face", "plank_timber", "damascus", "stitched_leather", "royal_cloth", "scales", "slate_shingle", "plaster", "cobble") else None
    if r is not None: return r
    return _shade_base(m, n)

def _shade_base(m, n):
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
