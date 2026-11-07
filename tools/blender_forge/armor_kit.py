"""Fantasy customisation kit for VRM-derived characters: measurement-driven armour plates (cuirass, pauldrons, bracers, greaves, belt),
draped sheet cloak, animal/elf ears, tails, staves and re-imported weapon GLBs.  Every piece is a separate Blender object named after the
engine body part it follows (torso_*, arm_l_*, forearm_r_*, shin_l_*, cloak_*, weapon_r_* ...) with its origin on that part's joint pivot."""
import os, sys, math
import numpy as np, bpy
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anatomy_core as ac, vrm_forge as vf
from anatomy_core import V

def _tag(ob, part):
    vf.tag_rigid(ob, part); return ob

def section(ch, z, part="torso", zw=.02):
    """Centre (x,y) and half extents (hx,hy) of the body at height z, measured from the vertices that follow `part`."""
    pts = np.vstack([s["V"][(np.abs(s["V"][:, 2] - z) < zw) & (s["j0"] == vf.PID[part])] for s in ch.verts])
    if len(pts) < 8: return np.array([0, 0.]), .14, .1
    lo, hi = np.percentile(pts[:, :2], 3, 0), np.percentile(pts[:, :2], 97, 0); return (lo + hi) / 2, (hi[0] - lo[0]) / 2, (hi[1] - lo[1]) / 2

def radius_at(ch, a, b, t, parts, tw=.07, rmax=.22, pct=72):
    a, b = np.array(a), np.array(b); d = b - a; L = np.linalg.norm(d); d /= L; rs = []
    for s in ch.verts:
        m = np.isin(s["j0"], [vf.PID[p] for p in parts]); q = s["V"][m] - a; u = q @ d / L; r = np.linalg.norm(q - np.outer(q @ d, d), axis=1)
        rs.append(r[(np.abs(u - t) < tw) & (r < rmax)])
    rs = np.concatenate(rs); return float(np.percentile(rs, pct)) if len(rs) > 5 else .05

def plate(ch, name, mat, part, a, b, t0, t1, parts, pad=.012, n=4, ref=(0, 1, 0), solid=.006, caps=(False, False), flare=1.0, rmax=.22):
    a, b = np.array(a), np.array(b); secs = []
    for t in np.linspace(t0, t1, n):
        r = radius_at(ch, a, b, t, parts, rmax=rmax) * (1 + (flare - 1) * (t - t0) / max(t1 - t0, 1e-3)) + pad; secs.append((V(tuple(a + (b - a) * t)), r, r))
    return _tag(ac.loft(name, secs, mat, segs=18, ref=ref, sub=1, pivot=V(tuple(ch.pivots[part])), caps=caps, solid=solid), part)

def cuirass(ch, name, mat, z0, z1, pad=.02, bulge=1.0, n=6, solid=.012):
    secs = []
    for i, z in enumerate(np.linspace(z0, z1, n)):
        c, hx, hy = section(ch, z); k = 1 + bulge * .07 * math.sin(math.pi * i / (n - 1)); secs.append((V((c[0], c[1], z)), (hy + pad) * k, (hx + pad) * k, 2.4))
    return _tag(ac.loft(name, secs, mat, segs=28, ref=(0, 0, 1), sub=1, pivot=V(tuple(ch.pivots["torso"])), caps=(False, False), solid=solid), "torso")

def pauldron(ch, side, mat, trim, layers=3, size=1.0):
    p = "arm_" + side; S = np.array(ch.pivots[p]); E = np.array(ch.pivots["forearm_" + side]); d = (E - S) / np.linalg.norm(E - S); sx = 1 if side == "l" else -1; k = ch.height / 1.8
    for i in range(layers):
        c = S + d * (.035 * i * k) + np.array([sx * .012, 0, .02 - .01 * i]) * k; sz = (1 - .1 * i) * size * k
        ac.OBJS  # noqa
        _tag(ac.prim("%s_pauldron%d" % (p, i), "sphere", mat, (.105 * sz, .095 * sz, .07 * sz), tuple(c), rot=(0, sx * -.5, 0), sub=1, pivot=V(tuple(S)), solid=.008, segs=20, keep=lambda q, c=c, i=i: q.z > c[2] - .045 * k), p)

def cloak(ch, mat, mat2, z_top=None, z_bot=None, spread=1.0, pad=.05, name="cloak_cape"):
    Pv = np.array(ch.pivots["cloak"]); z_top = z_top or Pv[2] + .03; z_bot = z_bot or ch.height * .30; grid = []
    for i, t in enumerate(np.linspace(0, 1, 11)):
        z = z_top + (z_bot - z_top) * t; c, hx, hy = section(ch, min(z, Pv[2] - .02)); row = []
        for j, u in enumerate(np.linspace(-1, 1, 13)):
            w = (hx + .045) * (1 + 1.1 * t * spread); ang = u * (.95 + .5 * t); x = c[0] + math.sin(ang) * w * 1.05
            y = c[1] + math.cos(ang) * (hy + pad + .22 * t * spread) + .014 * math.sin(u * 7 + t * 3) * t; row.append(V((x, y, z)))
        grid.append(row)
    return _tag(ac.sheet(name, grid, mat, sub=1, pivot=V(tuple(Pv)), solid=.008, mat2=mat2), "cloak")

def import_prop(path, part, ch, world_pos, dirn, length, roll=0.0, tag=None):
    """Re-import a Blender-built GLB (sword, shield ...), orient its long axis (+Z) along `dirn`, scale to `length`, and rebuild it as rigid objects of `part`."""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path); new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]; mn = np.array([1e9] * 3); mx = -mn
    for o in meshes:
        for v in o.bound_box: w = np.array(o.matrix_world @ Vector(v)); mn = np.minimum(mn, w); mx = np.maximum(mx, w)
    ext = mx - mn; ax = int(np.argmax(ext)); base = (mn + mx) / 2; base[ax] = mn[ax]
    R = Vector((0, 0, 1)).rotation_difference(Vector(dirn).normalized()).to_matrix().to_4x4() @ Matrix.Rotation(roll, 4, "Z")
    k = length / ext[ax]; piv = Vector(tuple(ch.pivots[part])); out = []
    axfix = {0: Matrix.Rotation(-math.pi / 2, 4, "Y"), 1: Matrix.Rotation(math.pi / 2, 4, "X"), 2: Matrix.Identity(4)}[ax]
    for o in meshes:
        M = Matrix.Translation(Vector(world_pos) - piv) @ R @ Matrix.Scale(k, 4) @ axfix @ Matrix.Translation(-Vector(base)) @ o.matrix_world
        o.parent = None; o.data.transform(M); o.matrix_world = Matrix.Identity(4); o.location = piv; o.name = "%s_%s" % (part, tag or "prop") + str(len(out)); out.append(_tag(o, part)); ac.OBJS.append(o)
    for o in new:
        if o.type != "MESH": bpy.data.objects.remove(o)
    return out

def cones(name, mat, part, ch, items, sub=1):
    """items: (position, (sx,sy,sz), euler) tuples -> ear/horn cones attached to `part`."""
    for i, (pos, sz, rot) in enumerate(items): _tag(ac.prim("%s%d" % (name, i), "cone", mat, sz, pos, rot=rot, sub=sub, pivot=V(tuple(ch.pivots[part])), segs=14, solid=.004), part)

def swoosh(name, mat, part, ch, pts, radii, flat=1.0):
    return _tag(ac.tube(name, [V(p) for p in pts], radii, mat, segs=10, flat=flat, sub=1, pivot=V(tuple(ch.pivots[part])), caps=(False, True)), part)

def hue_ramp(dark, light, gamma=1.0):
    def f(name, im):
        a = np.asarray(im).astype(float) / 255; lum = (a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11)[..., None] ** gamma
        rgb = np.array(dark) + (np.array(light) - np.array(dark)) * lum; a[..., :3] = np.clip(rgb, 0, 1)
        from PIL import Image; return Image.fromarray((a * 255).astype(np.uint8), "RGBA")
    return f

def knee(ch, side, mat, trim, size=1.0):
    K = np.array(ch.pivots["shin_" + side]); k = ch.height / 1.8; sx = 1 if side == "l" else -1
    _tag(ac.prim("shin_%s_kneecop" % side, "sphere", mat, (.052 * size * k, .04 * size * k, .058 * size * k), tuple(K + np.array([0, -.045 * k, .0])), sub=1, pivot=V(tuple(K)), solid=.006, segs=16), "shin_" + side)

def ear(ch, side, mat, base, length, width, tilt=-.35, spread=1.15, name="head_ear"):
    sx = 1 if side == "l" else -1; d = (Matrix.Rotation(sx * spread, 4, "Y") @ Matrix.Rotation(tilt, 4, "X")) @ Vector((0, 0, 1)); c = Vector(base) + d * length
    return _tag(ac.prim("%s_%s" % (name, side), "cone", mat, (width, width * .35, length), tuple(c), rot=(tilt, sx * spread, 0), sub=1, pivot=V(tuple(ch.pivots["head"])), segs=12, solid=.003), "head")

def shaft(ch, name, mat, part, p0, p1, r0, r1, n=6):
    p0, p1 = np.array(p0), np.array(p1); secs = [(V(tuple(p0 + (p1 - p0) * t)), r0 + (r1 - r0) * t, r0 + (r1 - r0) * t) for t in np.linspace(0, 1, n)]
    return _tag(ac.loft(name, secs, mat, segs=12, ref=(1, 0, 0), sub=1, pivot=V(tuple(ch.pivots[part])), caps=(True, True)), part)
