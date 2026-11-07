#!/usr/bin/env python3
"""Bake + export for SDF-sculpted creatures.  Pieces (V,F,N + per-vertex part weights) are grouped per material, unwrapped with Blender's
Smart UV Project, PBR-baked by rasterising every UV triangle in numpy (base colour, roughness/metal, emissive and a tangent-space normal
map derived from the material's height field), split per engine body part into named Blender objects whose origins are the joint pivots,
and exported through bpy.ops.export_scene.gltf (via vrm_forge.export_char)."""
import os, sys
import numpy as np, bpy
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anatomy_core as ac, vrm_forge as vf
import sdf_core as sc
PID, NAMES = vf.PID, vf.NAMES

_LAT = {}
def noise(P, s=1.0, seed=0):
    """smooth trilinear value noise in 0..1 (period 64 lattice cells; s = cells per metre/8)."""
    if seed not in _LAT: _LAT[seed] = ndi.gaussian_filter(np.random.default_rng(seed).random((64, 64, 64)).astype(np.float32), .6, mode="wrap")
    q = (np.asarray(P, np.float32) * (8 * s)) % 64; return ndi.map_coordinates(_LAT[seed], q.T, order=1, mode="wrap")

def fbm(P, s=1.0, oct=4, seed=0, gain=.5):
    a, t, r = 1.0, 0.0, 0.0
    for o in range(oct): r = r + a * noise(P, s * 2 ** o, seed + o); t += a; a *= gain
    return r / t

class Mat:
    """color(P,N)->(albedo n3, rough n, metal n, emit n3|None); height(P,N)->metres (normal-map relief)."""
    def __init__(s, name, color, height=None, nstr=1.0, double=False, mask=False, card=None, emit_str=1.0):
        s.name, s.color, s.height, s.nstr, s.double, s.mask, s.card, s.emit_str = name, color, height, nstr, double, mask, card, emit_str

class Model:
    def __init__(s, name, pivots, tex=1024):
        ac.reset(); ac.IMG_FMT = 'JPEG'; ac.EXPORT_TANGENTS = False; s.name, s.pivots, s.tex, s.pcs = name, {k: np.array(v, float) for k, v in pivots.items()}, tex, []
    def add(s, vfn, mat, part=None, segs=None, tau=.03, uv=None):
        V, F, N = vfn
        if len(F) == 0: return
        if part is not None: j0 = j1 = np.full(len(V), PID[part]); wb = np.zeros(len(V))
        else: j0, j1, wb = sc.weights(V, {PID[k]: v for k, v in segs.items()}, tau)
        s.pcs.append(dict(V=V, F=F, N=N, mat=mat, j0=j0, j1=j1, wb=wb, uv=uv))

    def _bake(s, mat, pcs):
        V, F, N = sc.merge([(p["V"], p["F"], p["N"]) for p in pcs]); n = 0; S0 = s.tex; j0, j1, wb = [], [], []
        for p in pcs: j0.append(p["j0"]); j1.append(p["j1"]); wb.append(p["wb"])
        j0, j1, wb = np.concatenate(j0), np.concatenate(j1), np.concatenate(wb); S = S0 if any(k in mat.name for k in ('skin', 'fur', 'cloth_main')) else max(256, S0 // 2)
        if mat.card is not None:
            uv = np.vstack([p["uv"] for p in pcs]); uvc = uv[F]; alb, ro, me, nm = mat.card(S)
            return V, F, N, uvc, j0, j1, wb, (alb, ro, me, nm, None)
        me_ = bpy.data.meshes.new("t"); me_.from_pydata(V.tolist(), [], F.tolist()); ob = bpy.data.objects.new("t", me_); bpy.context.collection.objects.link(ob)
        bpy.context.view_layer.objects.active = ob; ob.select_set(True); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.015); bpy.ops.object.mode_set(mode="OBJECT")
        u = np.zeros(len(me_.loops) * 2); me_.uv_layers.active.data.foreach_get("uv", u); uvc = u.reshape(-1, 3, 2); bpy.data.objects.remove(ob); bpy.data.meshes.remove(me_)
        cov = np.zeros((S, S), bool); alb = np.zeros((S, S, 3), np.float32); rm = np.zeros((S, S, 2), np.float32); nm = np.zeros((S, S, 3), np.float32); em = np.zeros((S, S, 3), np.float32); hasem = False
        TI, BY, X, Y = [], [], [], []
        for i in range(len(F)):
            q = uvc[i] * S; q = np.stack([q[:, 0], S - q[:, 1]], 1); x0, x1 = int(max(0, np.floor(q[:, 0].min()))), int(min(S - 1, np.ceil(q[:, 0].max())))
            y0, y1 = int(max(0, np.floor(q[:, 1].min()))), int(min(S - 1, np.ceil(q[:, 1].max())))
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + .5, np.arange(y0, y1 + 1) + .5); d = (q[1, 1] - q[2, 1]) * (q[0, 0] - q[2, 0]) + (q[2, 0] - q[1, 0]) * (q[0, 1] - q[2, 1])
            if abs(d) < 1e-9: continue
            l1 = ((q[1, 1] - q[2, 1]) * (gx - q[2, 0]) + (q[2, 0] - q[1, 0]) * (gy - q[2, 1])) / d; l2 = ((q[2, 1] - q[0, 1]) * (gx - q[2, 0]) + (q[0, 0] - q[2, 0]) * (gy - q[2, 1])) / d; l3 = 1 - l1 - l2
            m = (l1 >= -.02) & (l2 >= -.02) & (l3 >= -.02)
            if m.any(): k = int(m.sum()); TI.append(np.full(k, i)); BY.append(np.stack([l1[m], l2[m], l3[m]], 1)); X.append(gx[m].astype(int)); Y.append(gy[m].astype(int))
        TI, BY, X, Y = np.concatenate(TI), np.concatenate(BY), np.concatenate(X), np.concatenate(Y); X = np.clip(X, 0, S - 1); Y = np.clip(Y, 0, S - 1)
        e1 = V[F[:, 1]] - V[F[:, 0]]; e2 = V[F[:, 2]] - V[F[:, 0]]; d1 = uvc[:, 1] - uvc[:, 0]; d2 = uvc[:, 2] - uvc[:, 0]; r = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]; r = np.where(np.abs(r) < 1e-12, 1e-12, r)
        Tt = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) / r[:, None]; Bt = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) / r[:, None]
        for c0 in range(0, len(TI), 250000):
            sl = slice(c0, c0 + 250000); t, b = TI[sl], BY[sl]; Pp = np.einsum("ni,nij->nj", b, V[F[t]]); Nn = np.einsum("ni,nij->nj", b, N[F[t]]); Nn /= np.linalg.norm(Nn, axis=1, keepdims=True) + 1e-9
            T = Tt[t] - Nn * (Tt[t] * Nn).sum(1, keepdims=True); T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9; B = np.cross(Nn, T); B *= np.sign((B * Bt[t]).sum(1, keepdims=True) + 1e-12)
            col = mat.color(Pp, Nn); x, y = X[sl], Y[sl]; alb[y, x] = col[0]; rm[y, x, 0] = col[1]; rm[y, x, 1] = col[2]; cov[y, x] = True
            if col[3] is not None: em[y, x] = col[3]; hasem = True
            if mat.height is not None:
                e = .0025; h0 = mat.height(Pp, Nn); sT = (mat.height(Pp + e * T, Nn) - h0) / e * mat.nstr; sB = (mat.height(Pp + e * B, Nn) - h0) / e * mat.nstr
                nv = np.stack([-sT, -sB, np.ones_like(sT)], 1)
            else: nv = np.tile([0, 0, 1.], (len(t), 1))
            nm[y, x] = nv / np.linalg.norm(nv, axis=1, keepdims=True) * .5 + .5
        idx = ndi.distance_transform_edt(~cov, return_distances=False, return_indices=True)
        alb, rm, nm, em = alb[idx[0], idx[1]], rm[idx[0], idx[1]], nm[idx[0], idx[1]], em[idx[0], idx[1]]
        return V, F, N, uvc, j0, j1, wb, (alb, rm[..., 0], rm[..., 1], nm, em if hasem else None)

    def _material(s, mat, tx):
        alb, ro, me, nm, em = tx; key = s.name + "_" + mat.name
        m = bpy.data.materials.new(key); m.use_nodes = True; m.use_backface_culling = not mat.double; nt = m.node_tree; nt.nodes.clear()
        o = nt.nodes.new("ShaderNodeOutputMaterial"); b = nt.nodes.new("ShaderNodeBsdfPrincipled"); nt.links.new(b.outputs["BSDF"], o.inputs["Surface"])
        t1 = nt.nodes.new("ShaderNodeTexImage"); t1.image = ac._img(key + "_bc", alb, False); nt.links.new(t1.outputs["Color"], b.inputs["Base Color"])
        t2 = nt.nodes.new("ShaderNodeTexImage"); t2.image = ac._img(key + "_mr", np.dstack([np.ones_like(ro), ro, me]), True); sp = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(t2.outputs["Color"], sp.inputs["Color"]); nt.links.new(sp.outputs["Green"], b.inputs["Roughness"]); nt.links.new(sp.outputs["Blue"], b.inputs["Metallic"])
        t3 = nt.nodes.new("ShaderNodeTexImage"); t3.image = ac._img(key + "_nm", nm, True); nn = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(t3.outputs["Color"], nn.inputs["Color"]); nt.links.new(nn.outputs["Normal"], b.inputs["Normal"])
        if em is not None:
            t4 = nt.nodes.new("ShaderNodeTexImage"); t4.image = ac._img(key + "_em", em, False); nt.links.new(t4.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = mat.emit_str
        return m

    def export(s, path):
        groups = {}
        for p in s.pcs: groups.setdefault(p["mat"].name, (p["mat"], []))[1].append(p)
        ch = type("C", (), {})(); ch.mask = set(); objs = []
        for mname, (mat, pcs) in groups.items():
            V, F, N, uvc, j0, j1, wb, tx = s._bake(mat, pcs); bm = s._material(mat, tx)
            if mat.mask: ch.mask.add(bm.name)
            tp = j0[F]; maj = np.where(tp[:, 1] == tp[:, 2], tp[:, 1], tp[:, 0])
            for pid in np.unique(maj):
                sel = np.where(maj == pid)[0]; uq = np.unique(F[sel]); rm = -np.ones(len(V), int); rm[uq] = np.arange(len(uq)); pv = s.pivots[NAMES[pid]]
                me = bpy.data.meshes.new("m"); me.from_pydata((V[uq] - pv).tolist(), [], rm[F[sel]].tolist()); me.uv_layers.new(name="UVMap").data.foreach_set("uv", uvc[sel].reshape(-1, 2).ravel())
                q = me.uv_layers.new(name="skin"); a = np.stack([j0[uq].astype(float), 1.0 - (j1[uq] + wb[uq])], 1); q.data.foreach_set("uv", a[rm[F[sel]]].ravel())
                me.normals_split_custom_set(N[F[sel]].reshape(-1, 3).tolist()); me.materials.append(bm)
                ob = bpy.data.objects.new("%s_%s" % (NAMES[pid], mname), me); ob.location = pv.tolist(); bpy.context.collection.objects.link(ob); objs.append(ob)
        ac.OBJS.extend(objs); vf.export_char(path, ch)
        print("TRIS", sum(len(p["F"]) for p in s.pcs), "pieces", len(s.pcs), "materials", len(groups))
