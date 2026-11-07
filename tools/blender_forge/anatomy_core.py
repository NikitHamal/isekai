#!/usr/bin/env python3
"""Real Blender (bpy + bmesh + modifiers) anatomical modelling core: lofted limbs/torsos, tapered tubes, cloth sheets,
procedural PBR textures (albedo / normal / metal-rough) and articulated GLB export.  Blender space: Z up, character front = -Y,
character-right = -X (glTF export maps to Y-up, +Z forward)."""
import os, math, tempfile
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix
from scipy.ndimage import zoom, gaussian_filter

def V(*a):
    return Vector((0, 0, 0)) if not a else Vector(a[0] if len(a) == 1 else a)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_TMP = tempfile.mkdtemp(prefix="isekai_anat_")
_MATS = {}
OBJS = []

def reset():
    _MATS.clear(); OBJS.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------------------------------------------------------------- procedural textures
def _fbm(n, rng, scales=(4, 8, 16, 32), aniso=(1, 1), gain=0.55):
    acc = np.zeros((n, n)); amp = 1.0; tot = 0.0
    for s in scales:
        g = rng.random((max(2, int(s * aniso[0])), max(2, int(s * aniso[1]))))
        up = zoom(g, (n / g.shape[0], n / g.shape[1]), order=3, mode='grid-wrap', grid_mode=True)[:n, :n]
        acc += up * amp; tot += amp; amp *= gain
    acc /= tot
    return (acc - acc.min()) / (np.ptp(acc) + 1e-6)

def synth(kind, color, n=512, seed=1):
    """Return albedo(n,n,3), height(n,n), rough(n,n), metal(n,n) for a material kind."""
    rng = np.random.default_rng(seed); c = np.array(color[:3], float)
    yy, xx = np.mgrid[0:n, 0:n] / n
    base = _fbm(n, rng); fine = _fbm(n, rng, (64, 128, 192)); h = base * 0.4 + fine * 0.2
    rough = np.full((n, n), 0.6); metal = np.zeros((n, n)); tint = (0.82 + 0.36 * base)[..., None]
    if kind == "skin":
        pores = _fbm(n, rng, (96, 160)); tint = (0.93 + 0.14 * base)[..., None]
        alb = c * tint * (1 + 0.05 * (pores[..., None] - .5)); h = pores * 0.1 + base * 0.05; rough[:] = 0.52
        alb[..., 0] *= 1 + 0.06 * (_fbm(n, rng, (3, 6)) - .5)
    elif kind in ("cloth", "wool"):
        wv = (np.sin(xx * 220 * math.pi) * np.sin(yy * 220 * math.pi)) * 0.5 + 0.5
        folds = _fbm(n, rng, (3, 6), aniso=(1, 0.3)); tint = (0.78 + 0.35 * folds + 0.12 * fine)[..., None]
        alb = c * tint * (0.9 + 0.1 * wv[..., None]); h = wv * 0.35 + folds * 0.3; rough[:] = 0.86
    elif kind == "leather":
        cr = _fbm(n, rng, (24, 48, 96)); cell = np.abs(cr - gaussian_filter(cr, 2)) * 8
        alb = c * (0.7 + 0.5 * base + 0.2 * fine)[..., None] * (1 - 0.25 * np.clip(cell, 0, 1))[..., None]
        h = cr * 0.5 - np.clip(cell, 0, 1) * 0.4; rough = 0.55 + 0.3 * base
    elif kind in ("steel", "plate", "gold", "silver"):
        br = _fbm(n, rng, (2, 4, 8), aniso=(1, 24)); sc = _fbm(n, rng, (8, 16), aniso=(1, 40)) ** 3
        edge = np.clip(1 - 7 * np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy)), 0, 1)
        alb = c * (0.62 + 0.55 * br + 0.5 * sc + 0.12 * fine)[..., None] * (1 - 0.25 * edge[..., None]); h = br * 0.2 + sc * 0.4
        rough = 0.28 + 0.32 * (1 - br) + 0.15 * fine; metal = np.full((n, n), 0.95 if kind != "plate" else 0.85)
    elif kind == "hair":
        st = _fbm(n, rng, (3, 6, 12), aniso=(1, 80)); st2 = _fbm(n, rng, (2, 4), aniso=(1, 120))
        alb = c * (0.45 + 0.85 * st + 0.3 * st2)[..., None]; h = st * 0.5; rough[:] = 0.38
        alb = alb + np.array([.06, .07, .1]) * (st2 ** 4 * 3)[..., None]
    elif kind == "fur":
        st = _fbm(n, rng, (16, 48, 128), aniso=(1, 6)); blot = _fbm(n, rng, (3, 6, 12))
        alb = c * (0.42 + 0.9 * st * 0.6 + 0.6 * blot * 0.5)[..., None]; h = st * 0.8; rough[:] = 0.88
    elif kind == "orc":
        mt = _fbm(n, rng, (6, 12, 24)); sc = _fbm(n, rng, (40, 90))
        alb = c * (0.7 + 0.55 * mt)[..., None] * (1 + 0.1 * (sc[..., None] - .5)); alb[..., 0] *= 1 + 0.25 * (mt - .5)
        h = sc * 0.5 + mt * 0.3; rough[:] = 0.64
    elif kind == "bone":
        alb = c * (0.78 + 0.35 * base + 0.2 * fine)[..., None]; h = fine * 0.5; rough[:] = 0.7
    elif kind == "glow":
        alb = c * (0.9 + 0.2 * base)[..., None]; h = base * 0.1; rough[:] = 0.2
    else:
        alb = c * tint; rough[:] = 0.7
    return np.clip(alb, 0, 1), np.clip(h, 0, 1), np.clip(rough, 0.04, 1), np.clip(metal, 0, 1)

def _img(name, arr, noncolor):
    from PIL import Image
    path = os.path.join(_TMP, name + ".png")
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(path)
    im = bpy.data.images.load(path); im.colorspace_settings.name = "Non-Color" if noncolor else "sRGB"; im.pack()
    return im

def material(key, kind, color, n=512, seed=1, nstr=3.0, rough=None, metal=None, emit=None, emit_str=1.0, double=False):
    if key in _MATS: return _MATS[key]
    alb, h, ro, me = synth(kind, color, n, seed)
    if rough is not None: ro = ro * 0 + rough
    if metal is not None: me = me * 0 + metal
    gy, gx = np.gradient(gaussian_filter(h, 0.7)); nrm = np.dstack([-gx * nstr * n / 64, gy * nstr * n / 64, np.ones_like(h)])
    nrm = nrm / np.linalg.norm(nrm, axis=2, keepdims=True) * 0.5 + 0.5
    mr = np.dstack([np.ones_like(h), ro, me])
    m = bpy.data.materials.new(key); m.use_nodes = True; m.use_backface_culling = not double
    nt = m.node_tree; nt.nodes.clear(); o = nt.nodes.new("ShaderNodeOutputMaterial"); b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(b.outputs["BSDF"], o.inputs["Surface"])
    t1 = nt.nodes.new("ShaderNodeTexImage"); t1.image = _img(key + "_bc", alb, False); nt.links.new(t1.outputs["Color"], b.inputs["Base Color"])
    t2 = nt.nodes.new("ShaderNodeTexImage"); t2.image = _img(key + "_mr", mr, True)
    sp = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(t2.outputs["Color"], sp.inputs["Color"])
    nt.links.new(sp.outputs["Green"], b.inputs["Roughness"]); nt.links.new(sp.outputs["Blue"], b.inputs["Metallic"])
    t3 = nt.nodes.new("ShaderNodeTexImage"); t3.image = _img(key + "_nm", nrm, True)
    nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(t3.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    if emit is not None:
        e = np.clip(np.array(emit[:3], float) * (0.55 + 0.9 * h[..., None]), 0, 1)
        t4 = nt.nodes.new("ShaderNodeTexImage"); t4.image = _img(key + "_em", e, False)
        nt.links.new(t4.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emit_str
    _MATS[key] = m
    return m

# ---------------------------------------------------------------- mesh helpers
def _frame(t, ref):
    t = V(t).normalized(); r = V(ref)
    if abs(t.dot(r.normalized())) > 0.97: r = V((1, 0, 0)) if abs(t.x) < 0.9 else V((0, 1, 0))
    u = r.cross(t).normalized(); v = t.cross(u).normalized(); return u, v

def _ring(c, u, v, rx, ry, segs, pw=2.0, shift=0.0):
    pts = []
    for k in range(segs):
        a = 2 * math.pi * k / segs; ca, sa = math.cos(a), math.sin(a)
        x = rx * math.copysign(abs(ca) ** (2 / pw), ca); y = ry * math.copysign(abs(sa) ** (2 / pw), sa)
        pts.append(V(c) + u * x + v * (y + shift))
    return pts

def loft(name, secs, mat, segs=14, ref=(0, 1, 0), tile=0.5, sub=1, pivot=None, caps=(True, True), closed=False, keep=None,
         solid=None, smooth=True, bevel=None, mat2=None):
    """secs: list of (center, rx, ry[, power[, shift_v]]). Builds one lofted mesh object with direct cylindrical UVs."""
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap"); rings = []; dist = [0.0]; n = len(secs)
    P = [V(s[0]) for s in secs]
    for i, s in enumerate(secs):
        if closed: t = P[(i + 1) % n] - P[(i - 1) % n]
        else: t = P[min(i + 1, n - 1)] - P[max(i - 1, 0)]
        u, v = _frame(t, ref); pw = s[3] if len(s) > 3 else 2.0; sh = s[4] if len(s) > 4 else 0.0
        rings.append([bm.verts.new(p) for p in _ring(P[i], u, v, max(s[1], 1e-4), max(s[2], 1e-4), segs, pw, sh)])
        if i: dist.append(dist[-1] + (P[i] - P[i - 1]).length)
    if closed: dist.append(dist[-1] + (P[0] - P[-1]).length)
    last = n if closed else n - 1; circ = [2 * math.pi * 0.5 * (s[1] + s[2]) for s in secs]
    for i in range(last):
        j = (i + 1) % n
        for k in range(segs):
            k2 = (k + 1) % segs
            try: f = bm.faces.new((rings[i][k], rings[i][k2], rings[j][k2], rings[j][k]))
            except ValueError: continue
            if keep is not None:
                c = sum((vv.co for vv in f.verts), V()) / 4
                if not keep(c): bm.faces.remove(f); continue
            for lp, (kk, ii) in zip(f.loops, ((k, i), (k + 1, i), (k + 1, i + 1), (k, i + 1))):
                lp[uv].uv = (kk / segs * circ[i] / tile, (dist[ii] if ii < len(dist) else dist[-1]) / tile)
    if not closed:
        for idx, (ring, on) in enumerate(((rings[0], caps[0]), (rings[-1], caps[1]))):
            if on:
                try: f = bm.faces.new(ring[::-1] if idx == 0 else ring)
                except ValueError: continue
                for lp in f.loops: lp[uv].uv = (lp.vert.co.x / tile + .5, lp.vert.co.y / tile + .5)
    bm.normal_update(); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return _finish(name, bm, mat, sub, pivot, solid, smooth, bevel, mat2)

def tube(name, pts, radii, mat, segs=8, flat=1.0, **kw):
    """Tapered tube along arbitrary 3D points; flat<1 flattens the section (hair clumps, lips, brows)."""
    return loft(name, [(p, r, r * flat) for p, r in zip(pts, radii)], mat, segs=segs, **kw)

def sheet(name, grid, mat, sub=0, pivot=None, solid=0.01, mat2=None, smooth=True):
    """grid: 2D list [rows][cols] of Vectors -> cloth sheet with UVs (solidify gives thickness + inner material)."""
    bm = bmesh.new(); uv = bm.loops.layers.uv.new("UVMap"); R = len(grid); C = len(grid[0])
    vs = [[bm.verts.new(p) for p in row] for row in grid]
    for i in range(R - 1):
        for k in range(C - 1):
            f = bm.faces.new((vs[i][k], vs[i][k + 1], vs[i + 1][k + 1], vs[i + 1][k]))
            for lp, (ii, kk) in zip(f.loops, ((i, k), (i, k + 1), (i + 1, k + 1), (i + 1, k))):
                lp[uv].uv = (kk / (C - 1) * 1.2, 1 - ii / (R - 1))
    bm.normal_update()
    return _finish(name, bm, mat, sub, pivot, solid, smooth, None, mat2)

def prim(name, kind, mat, size=(1, 1, 1), loc=(0, 0, 0), rot=(0, 0, 0), sub=1, pivot=None, solid=None, segs=16, bevel=None, keep=None, mat2=None):
    """Primitive via bmesh (sphere/cube/cone/cyl) with scale, euler rotation and Blender modifiers; Smart UV Project."""
    bm = bmesh.new()
    if kind == "sphere": bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=max(6, segs // 2), radius=1.0)
    elif kind == "cube": bmesh.ops.create_cube(bm, size=2.0)
    elif kind == "cone": bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=1.0, radius2=0.0, depth=2.0)
    elif kind == "cyl": bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=1.0, radius2=1.0, depth=2.0)
    R = (Matrix.Rotation(rot[2], 4, 'Z') @ Matrix.Rotation(rot[1], 4, 'Y') @ Matrix.Rotation(rot[0], 4, 'X'))
    S = Matrix.Diagonal((size[0], size[1], size[2], 1))
    bmesh.ops.transform(bm, matrix=Matrix.Translation(loc) @ R @ S, verts=bm.verts)
    if keep is not None:
        dead = [f for f in bm.faces if not keep(f.calc_center_median())]
        bmesh.ops.delete(bm, geom=dead, context='FACES_ONLY')
    bm.normal_update(); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return _finish(name, bm, mat, sub, pivot, solid, True, bevel, mat2, smart=True)

def _finish(name, bm, mat, sub, pivot, solid, smooth, bevel, mat2, smart=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    if mat2 is not None: ob.data.materials.append(mat2)
    if smart or not me.uv_layers:
        bpy.context.view_layer.objects.active = ob; ob.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02); bpy.ops.object.mode_set(mode='OBJECT'); ob.select_set(False)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    if solid:
        m = ob.modifiers.new("Solidify", 'SOLIDIFY'); m.thickness = solid; m.offset = 0.0
        if mat2 is not None: m.material_offset = 1
    if bevel:
        m = ob.modifiers.new("Bevel", 'BEVEL'); m.width = bevel; m.segments = 2; m.limit_method = 'ANGLE'
    if sub:
        m = ob.modifiers.new("Subsurf", 'SUBSURF'); m.levels = sub; m.render_levels = sub
    ob.modifiers.new("Triangulate", 'TRIANGULATE')
    if pivot is not None:
        pv = V(pivot); me.transform(Matrix.Translation(-pv)); ob.location = pv
    OBJS.append(ob); return ob

def sculpt(ob, fn):
    """In-place bmesh sculpt: fn(vertex_world_co) -> displacement Vector (before modifiers)."""
    bm = bmesh.new(); bm.from_mesh(ob.data); off = ob.location
    for v in bm.verts: v.co += fn(v.co + off)
    bm.to_mesh(ob.data); bm.free(); ob.data.update()

def mirror_x(ob, name):
    """Real geometric mirror copy across X (character left<->right) with mirrored pivot and flipped winding."""
    me = ob.data.copy(); n = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(n)
    n.location = V((-ob.location.x, ob.location.y, ob.location.z)); bm = bmesh.new(); bm.from_mesh(me)
    for v in bm.verts: v.co.x = -v.co.x
    bmesh.ops.reverse_faces(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    for md in ob.modifiers:
        m2 = n.modifiers.new(md.name, md.type)
        for a in ("levels", "render_levels", "thickness", "offset", "material_offset", "width", "segments", "limit_method"):
            if hasattr(md, a): setattr(m2, a, getattr(md, a))
    OBJS.append(n); return n

def export(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_yup=True, export_apply=True, export_normals=True,
                              export_texcoords=True, export_tangents=True, export_materials='EXPORT', export_cameras=False, export_lights=False)
    dg = bpy.context.evaluated_depsgraph_get(); t = 0
    for o in OBJS:
        e = o.evaluated_get(dg); me = e.to_mesh(); t += sum(len(p.vertices) - 2 for p in me.polygons); e.to_mesh_clear()
    print("EXPORTED", path, "objects=%d tris=%d" % (len(OBJS), t))
    return path

def join(objs, name):
    """Join objects (same pivot/material set) into one Blender mesh object using bpy.ops.object.join."""
    objs = [o for o in objs if o is not None]
    if len(objs) < 2: return objs[0] if objs else None
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); ob = bpy.context.view_layer.objects.active; ob.name = name
    for o in objs[1:]:
        if o in OBJS: OBJS.remove(o)
    ob.select_set(False); return ob
