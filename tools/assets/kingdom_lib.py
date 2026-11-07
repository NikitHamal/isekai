"""Shared materials + architectural/armour helpers for the Valoria Kingdom asset set (all metres, +Z = front, origin at the feet/ground)."""
from common import *
import numpy as np
CASTLE = Material("castle_masonry", "cut_stone", (.64, .62, .57), (.37, .36, .33), rough=.93, scale=9, bump=4.5, seed=61)
STONEF = Material("hewn_stone_blocks", "stone_face", (.66, .63, .57), (.4, .38, .34), rough=.92, scale=3, bump=4, seed=62)
DARKSTONE = Material("dark_plinth_stone", "stone_face", (.42, .41, .39), (.25, .25, .24), rough=.95, scale=3, bump=4, seed=63)
OAKP = Material("rough_oak_planks", "plank_timber", (.45, .3, .17), (.2, .12, .06), rough=.82, scale=8, bump=4, seed=64)
BEAM = Material("aged_oak_beam", "wood_grain", (.3, .19, .1), (.14, .08, .04), rough=.85, scale=6, bump=3, seed=65)
SLATE = Material("slate_shingles", "slate_shingle", (.26, .29, .35), (.12, .14, .19), rough=.7, scale=14, bump=4, seed=66)
PLASTER = Material("lime_plaster", "plaster", (.86, .81, .7), (.62, .57, .46), rough=.95, scale=4, bump=2, seed=67)
GLASSLIT = Material("leaded_glass_lit", "fbm_noise", (.95, .7, .3), (.7, .45, .15), rough=.2, emissive=(1, .6, .24), scale=6, bump=.6, seed=68)
DAMASK = Material("damascus_steel", "damascus", (.78, .8, .86), (.33, .36, .44), rough=.32, metal=1.0, scale=6, bump=2.5, seed=69)
DARKSTEEL = Material("blackened_iron", "hammered_metal", (.24, .24, .27), (.1, .1, .12), rough=.55, metal=.9, scale=5, bump=2, seed=70)
LEATHERS = Material("stitched_leather", "stitched_leather", (.26, .15, .08), (.11, .06, .03), rough=.62, scale=5, bump=3, seed=71)
GAMBE = Material("quilted_gambeson", "woven_cloth", (.15, .15, .18), (.07, .07, .09), rough=.9, scale=9, bump=3, seed=72)
CLOAKB = Material("midnight_cloak", "woven_cloth", (.05, .08, .27), (.02, .03, .12), rough=.88, scale=7, bump=2.5, seed=73)
CLOAKR = Material("crimson_lining", "woven_cloth", (.5, .04, .07), (.26, .02, .04), rough=.85, scale=7, bump=2.5, seed=74)
BANNER = Material("royal_banner", "royal_cloth", (.6, .04, .08), (.32, .02, .05), rough=.9, scale=5, bump=2, seed=75)
CANVAS = Material("weathered_canvas", "woven_cloth", (.82, .76, .6), (.58, .52, .38), rough=.95, scale=8, bump=2.5, seed=76)
ORCSKIN = Material("orc_skin", "fbm_noise", (.3, .4, .19), (.15, .22, .09), rough=.75, scale=9, bump=2.5, seed=77)
FURM = Material("shadow_fur", "fbm_noise", (.11, .11, .15), (.03, .03, .05), rough=.95, scale=40, bump=3, seed=78)
BONEM = Material("bone", "fbm_noise", (.86, .8, .66), (.6, .54, .42), rough=.6, scale=6, bump=1.5, seed=79)
SHADOWEYE = Material("shadow_eye", "runic_glow", (.7, .2, 1), (.4, .1, .8), rough=.2, emissive=(.8, .25, 1), scale=3, seed=80)
FLESH = Material("skin_tone", "fbm_noise", (.9, .7, .58), (.78, .56, .45), rough=.6, scale=4, bump=.4, seed=81)
DARKHAIR = Material("dark_hair", "wood_grain", (.07, .06, .08), (.03, .03, .04), rough=.5, scale=14, bump=2, seed=82)
GOLDM = Material("royal_gold", "hammered_metal", (.95, .75, .3), (.7, .5, .15), rough=.28, metal=1.0, scale=6, bump=1.2, seed=83)
CRIMSONCLOTH = Material("surcoat_crimson", "royal_cloth", (.62, .05, .08), (.34, .02, .05), rough=.88, scale=6, bump=2, seed=84)
def scale_uv(m, su, sv): m.UV = m.UV * np.array([su, sv]); return m
def box_tri(size, pos=(0, 0, 0), rot=(0, 0, 0), d=.3, seg=1):
    """Box whose UVs are world-density mapped (d = texture repeats per metre) so large walls keep a real-world block size."""
    b = box((1, 1, 1), seg=seg); N = b.normals(); V = b.V * np.asarray(size, float); ax = np.abs(N).argmax(1)
    u = np.where(ax == 0, V[:, 2], V[:, 0]); v = np.where(ax == 1, V[:, 2], V[:, 1]); b.UV = np.stack([u, v], 1) * d
    return b.tf(pos, rot, size)
def cyl_tri(r, h, pos=(0, 0, 0), d=.3, sides=28, r2=None, rings=1, cap=True, rot=(0, 0, 0)):
    m = cylinder(r, h, sides=sides, r2=r2, rings=rings, cap=cap); su = max(1, round(2 * np.pi * r * d)); m.UV = m.UV * np.array([su, h * d]); return m.tf(pos, rot)
def block_wall(x0, x1, y0, y1, z, thick, ch=.34, bl=.75, seed=1, d=.5, relief=.06, axis=0, holes=()):
    """Individually modelled hewn stone blocks (running bond) with randomised relief. axis 0: wall runs along X at depth z; axis 1: runs along Z at x=z."""
    r = np.random.RandomState(seed); parts = []; y = y0; j = 0
    while y < y1 - 1e-3:
        h = min(ch * (.9 + .2 * r.rand()), y1 - y); x = x0 - r.rand() * bl * .5
        while x < x1 - 1e-3:
            L = bl * (.75 + .6 * r.rand()); xa = max(x, x0); xb = min(x + L, x1)
            hit = any(xa < hb and xb > ha and y < yb and y + h > ya for ha, hb, ya, yb in holes)
            if xb - xa > .05 and not hit:
                t = thick * (.9 + relief * 4 * r.rand()); c = (.5 * (xa + xb), y + h / 2, z + (t - thick) / 2)
                if axis == 0: parts.append(box_tri((xb - xa - .02, h - .02, t), c, (0, 0, 0), d))
                else: parts.append(box_tri((t, h - .02, xb - xa - .02), (z + (t - thick) / 2, c[1], c[0]), (0, 0, 0), d))
            x += L
        y += h; j += 1
    return merge(parts)
def crenellations(x0, x1, y, z, thick, mw=.7, mh=.75, gap=.55, axis=0, seed=2):
    parts = []; x = x0; r = np.random.RandomState(seed)
    while x + mw <= x1 + 1e-3:
        c = x + mw / 2; parts.append(box_tri((mw, mh, thick), (c, y + mh / 2, z), d=.5) if axis == 0 else box_tri((thick, mh, mw), (z, y + mh / 2, c), d=.5)); x += mw + gap
    return merge(parts)
def round_tower(r, h, pos, seed=3, d=.32, battlements=True):
    """Cylindrical masonry tower: faceted hewn-stone ring courses, corbelled crown, crenellated parapet and a conical-free open top."""
    px, py, pz = pos; parts = [cyl_tri(r, h, (px, py + h / 2, pz), d, 40, rings=2)]
    n = int(h / .9); rr = np.random.RandomState(seed)
    for k in range(n):
        a0 = rr.rand() * 6.28
        for i in range(9):
            a = a0 + i * 2 * np.pi / 9 + .1 * rr.randn(); parts.append(box_tri((.7, .4, .12), (px + np.cos(a) * (r + .03), py + .45 + k * .9, pz + np.sin(a) * (r + .03)), (0, -np.degrees(a) + 90, 0), .5))
    parts.append(cyl_tri(r + .35, .6, (px, py + h + .1, pz), d, 40, r2=r + .1, rings=2)); parts.append(cyl_tri(r + .35, .22, (px, py + h + .5, pz), d, 40))
    if battlements:
        for i in range(12):
            a = i * 2 * np.pi / 12; parts.append(box_tri((.75, .85, .5), (px + np.cos(a) * (r + .15), py + h + .6 + .43, pz + np.sin(a) * (r + .15)), (0, -np.degrees(a) + 90, 0), .5))
    return merge(parts)
def arch_opening(cx, y0, w, h, z, thick, n=13, seed=4, d=.5):
    """Round-arch voussoir ring (individual wedge-ish blocks) over an opening of width w; springs at y0+h."""
    R = w / 2; parts = []
    for i in range(n):
        a = np.pi * (i + .5) / n; arc = np.pi * (R + .3) / n
        parts.append(box_tri((.42, arc * 1.04, thick), (cx + np.cos(np.pi - a) * (R + .21), y0 + h + np.sin(np.pi - a) * (R + .21), z), (0, 0, np.degrees(np.pi - a)), d))
    return merge(parts)
def beam(a, b, w=.2, d=.8):
    a = np.asarray(a, float); b = np.asarray(b, float); L = np.linalg.norm(b - a); v = (b - a) / L
    yaw = np.degrees(np.arctan2(v[0], v[2])); pitch = -np.degrees(np.arcsin(v[1])); return box_tri((w, w, L), (a + b) / 2, (pitch, yaw, 0), d).tf() if False else _beam(a, b, w, L, d)
def _beam(a, b, w, L, d):
    v = (b - a) / L; m = box_tri((w, w, L), (0, 0, 0), (0, 0, 0), d)
    # rotate +Z onto v
    z = np.array([0, 0, 1.]); ax = np.cross(z, v); s = np.linalg.norm(ax); c = z @ v
    if s < 1e-9: Rm = np.eye(3) if c > 0 else np.diag([1, -1, -1.])
    else:
        k = ax / s; K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]]); Rm = np.eye(3) + K * s + K @ K * (1 - c)
    return Mesh(m.V @ Rm.T + (a + b) / 2, m.F.copy(), m.UV.copy())
def tube(a, b, r, sides=14, d=.8, r2=None):
    a = np.asarray(a, float); b = np.asarray(b, float); L = np.linalg.norm(b - a); v = (b - a) / L; m = cylinder(r, L, sides=sides, r2=r2, rings=1)
    m.UV = m.UV * np.array([max(1, round(2 * np.pi * r * d)), L * d]); y = np.array([0, 1., 0]); ax = np.cross(y, v); s = np.linalg.norm(ax); c = y @ v
    if s < 1e-9: Rm = np.eye(3) if c > 0 else np.diag([1, -1, -1.])
    else:
        k = ax / s; K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]]); Rm = np.eye(3) + K * s + K @ K * (1 - c)
    return Mesh(m.V @ Rm.T + (a + b) / 2, m.F.copy(), m.UV.copy())
def ell(c, r, rings=14, sides=20, uv=1.0, rot=(0, 0, 0)):
    m = sphere(1, (0, 0, 0), r, rings, sides, rot=rot); m.UV = m.UV * uv; return m.tf(c)
def poly_prism(poly, t, pos=(0, 0, 0), d=.4, rot=(0, 0, 0)):
    """Extrude a convex 2D polygon [(x,y)...] by thickness t along Z (flat-shaded faces, outward winding, world-density UVs)."""
    P = np.asarray(poly, float); n = len(P); c = P.mean(0); parts = []
    def face(vs, uvf):
        vs = np.asarray(vs, float); cen = vs.mean(0) - np.array([c[0], c[1], 0]); F = np.array([[0, i, i + 1] for i in range(1, len(vs) - 1)])
        nrm = np.cross(vs[F[0, 1]] - vs[F[0, 0]], vs[F[0, 2]] - vs[F[0, 0]])
        if nrm @ (vs.mean(0) - np.array([c[0], c[1], 0])) < 0: F = F[:, ::-1]
        parts.append(Mesh(vs, F, np.array([uvf(v) for v in vs])))
    z0, z1 = -t / 2, t / 2
    face([[x, y, z1] for x, y in P], lambda v: (v[0] * d, v[1] * d)); face([[x, y, z0] for x, y in P], lambda v: (v[0] * d, v[1] * d))
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]; L = np.linalg.norm(b - a); face([[a[0], a[1], z0], [b[0], b[1], z0], [b[0], b[1], z1], [a[0], a[1], z1]], lambda v, a=a: (v[2] * d, np.linalg.norm(v[:2] - a) * d))
    return merge(parts).tf(pos, rot)
def gable_roof(L, half_w, rise, pos=(0, 0, 0), over=.5, thick=.28, d=.26, lip_rows=14, mat_slate=None):
    """Steep gable roof along X: two thick slate slabs, ridge cap, overlapping course lips. Returns (slate_mesh, ridge_mesh)."""
    ang = np.degrees(np.arctan2(rise, half_w)); slope = np.hypot(half_w, rise) + over; parts = []; ridge = []
    for sg in (-1, 1):
        cy = rise / 2; cz = sg * half_w / 2; ca, sa = np.cos(np.radians(ang)), np.sin(np.radians(ang)); cen = np.array([0, cy - .14, cz + sg * over * .35 * ca])
        parts.append(box_tri((L, thick, slope), cen, (sg * ang, 0, 0), d))
        nrm = np.array([0, ca, sg * sa]); down = np.array([0, -sa, sg * ca])
        for k in range(lip_rows):
            s_ = ((k + .5) / lip_rows - .5) * (slope - .6); p = cen + down * s_ + nrm * (thick / 2 + .02)
            parts.append(box_tri((L - .2, .07, slope / lip_rows * 1.15), p, (sg * ang, 0, 0), d * 2))
    ridge.append(cyl_tri(.2, L + .4, (0, rise + .02, 0), .8, 12, rot=(0, 0, 90)))
    return merge(parts).tf(pos), merge(ridge).tf(pos)
