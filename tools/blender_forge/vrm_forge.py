"""VRM (VRoid anime avatar) -> Isekai part-rig GLB, done with real headless Blender (bpy).
Pipeline: import the CC0/free VRoid sample through Blender's glTF importer, read the skin weights, rotate to engine facing (-Y), scale to
game height, lower the arms from T-pose to A-pose (linear blend skinning), convert every vertex's bone weights into the engine's 14 named body
parts (top-2 part influences stored in UV set 2 -> TEXCOORD_1 = (part0, part1 + blend)), split the mesh per material+part into named Blender
objects with joint pivots as origins, rebuild materials (PNG <= 1024px, flat normal + MR maps, alpha-mask for hair cards) and export via
bpy.ops.export_scene.gltf.  Customisation hooks: texture tint callback, hair/skirt sway part, extra rigid armour pieces (armor_kit.py)."""
import os, sys, math, shutil
import numpy as np, bpy
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anatomy_core as ac

PID = dict(torso=1, head=2, cloak=3, arm_l=4, arm_r=5, leg_l=6, leg_r=7, weapon_r=8, tail=9, forearm_l=10, forearm_r=11, shin_l=12, shin_r=13)
NAMES = {v: k for k, v in PID.items()}
TEX = "/tmp/vrm_tex"; os.makedirs(TEX, exist_ok=True)

def bone_part(n, hair="head", skirt="cloak"):
    if n.startswith("J_Bip_"):
        s, k = n[6].lower(), n[8:]
        if k in ("Neck", "Head"): return "head"
        if k == "UpperArm": return "arm_" + s
        if k in ("LowerArm", "Hand") or k[:-1] in ("Index", "Little", "Middle", "Ring", "Thumb"): return "forearm_" + s
        if k == "UpperLeg": return "leg_" + s
        if k in ("LowerLeg", "Foot", "ToeBase"): return "shin_" + s
        return "torso"
    if "FaceEye" in n: return "head"
    if "Hair" in n: return hair
    if "Skirt" in n or "Coat" in n: return skirt
    if "Sleeve" in n: return "forearm_" + n[6].lower()
    return "torso"

def Ry(t): c, s = math.cos(t), math.sin(t); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

def _png(img, name, maxs=1024, tint=None):
    p = os.path.join(TEX, name + "_raw.png"); img.filepath_raw = p; img.file_format = "PNG"; img.save()
    im = Image.open(p).convert("RGBA")
    if max(im.size) > maxs: k = maxs / max(im.size); im = im.resize((max(8, int(im.size[0] * k)), max(8, int(im.size[1] * k))), Image.LANCZOS)
    if tint: im = tint(name, im)
    mask = np.asarray(im)[..., 3].min() < 250
    if not mask: im.putalpha(255)
    out = os.path.join(TEX, name + ".png"); im.save(out); return out, mask

def _flat(name, rgb):
    p = os.path.join(TEX, name + ".png"); Image.new("RGB", (8, 8), rgb).save(p); return p

def make_mat(name, png, mask, rough=0.82, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new("ShaderNodeOutputMaterial"); b = nt.nodes.new("ShaderNodeBsdfPrincipled"); nt.links.new(b.outputs["BSDF"], o.inputs["Surface"])
    def tex(path, nc):
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path, check_existing=True); t.image.colorspace_settings.name = "Non-Color" if nc else "sRGB"; t.image.pack(); return t
    t1 = tex(png, False); nt.links.new(t1.outputs["Color"], b.inputs["Base Color"])
    if mask:
        nt.links.new(t1.outputs["Alpha"], b.inputs["Alpha"])
        try: m.blend_method = "CLIP"; m.alpha_threshold = 0.5
        except Exception: pass
        if hasattr(m, "surface_render_method"): m.surface_render_method = "DITHERED"
    t2 = tex(_flat("flat_mr_%d" % int(rough * 100), (255, int(rough * 255), 0)), True); sp = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(t2.outputs["Color"], sp.inputs["Color"]); nt.links.new(sp.outputs["Green"], b.inputs["Roughness"]); nt.links.new(sp.outputs["Blue"], b.inputs["Metallic"])
    t3 = tex(_flat("flat_nm", (128, 128, 255)), True); nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(t3.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    if emit:
        b.inputs["Emission Strength"].default_value = 1.0; t4 = tex(emit, False); nt.links.new(t4.outputs["Color"], b.inputs["Emission Color"])
    m.use_backface_culling = False; return m

class Char: pass

def convert(path, height, name, hair="head", skirt="cloak", arm_drop=1.12, skirt_leg=0.6, tint=None, rough=0.82):
    ac.reset(); shutil.copy(path, "/tmp/_vrm_in.glb"); bpy.ops.import_scene.gltf(filepath="/tmp/_vrm_in.glb")
    arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]; bn = [b.name for b in arm.data.bones]; bi = {n: i for i, n in enumerate(bn)}
    flip = np.array([-1, -1, 1.0]); bones = {b.name: np.array(arm.matrix_world @ b.head_local) * flip for b in arm.data.bones}
    parts = sorted(PID, key=PID.get); B2P = np.zeros((len(bn), len(parts)), np.float32)
    for n in bn: B2P[bi[n], parts.index(bone_part(n, hair, skirt))] = 1
    skirtB = np.array([("Skirt" in n or "Coat" in n) for n in bn], np.float32)
    def isarm(n, s): return (n.startswith("J_Bip_" + s.upper()) and n[8:] != "Shoulder" and not any(x in n for x in ("Leg", "Foot", "Toe"))) or (("_Sec_" + s.upper() + "_") in n and "Sleeve" in n)
    armB = {s: np.array([1.0 if isarm(n, s) else (.85 if n == "J_Bip_%s_Shoulder" % s.upper() else 0.) for n in bn], np.float32) for s in "lr"}
    srcs, mats = [], {}
    for o in [o for o in bpy.data.objects if o.type == "MESH" and len(o.vertex_groups) > 0]:
        me = o.data; N = len(me.vertices); W = np.zeros((N, len(bn)), np.float32); vg = [g.name for g in o.vertex_groups]
        for v in me.vertices:
            for g in v.groups:
                if vg[g.group] in bi: W[v.index, bi[vg[g.group]]] = g.weight
        V = np.zeros(N * 3); me.vertices.foreach_get("co", V); me.calc_loop_triangles(); lt = me.loop_triangles; T = len(lt)
        tl, tv, tm = np.zeros(T * 3, np.int32), np.zeros(T * 3, np.int32), np.zeros(T, np.int32); lt.foreach_get("loops", tl); lt.foreach_get("vertices", tv); lt.foreach_get("material_index", tm)
        L = len(me.loops); uv = np.zeros(L * 2); me.uv_layers.active.data.foreach_get("uv", uv); nr = np.zeros(L * 3); me.corner_normals.foreach_get("vector", nr); lv = np.zeros(L, np.int32); me.loops.foreach_get("vertex_index", lv)
        for i, m in enumerate(me.materials):
            if m.name not in mats:
                im = [n.image for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image][0]; sn = m.name.replace(" (Instance)", "").split("_", 3)[-1]
                png, mk = _png(im, name + "_" + sn, tint=tint); mats[m.name] = (sn, png, mk)
        srcs.append(dict(W=W, V=V.reshape(-1, 3) * flip, tl=tl.reshape(-1, 3), tv=tv.reshape(-1, 3), tm=tm, uv=uv.reshape(-1, 2), nr=nr.reshape(-1, 3) * flip, mn=[m.name for m in me.materials], nm=o.name, lv=lv))
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    allv = np.vstack([s["V"] for s in srcs]); z0 = allv[:, 2].min(); head_top = max(s["V"][:, 2].max() for s in srcs if s["nm"] == "Face")
    k = height / (head_top - z0); shift = np.array([0, 0, -z0])
    for s in srcs: s["V"] = (s["V"] + shift) * k
    for n in bones: bones[n] = (bones[n] + shift) * k
    for side, sg in (("l", 1), ("r", -1)):   # T-pose -> A-pose: LBS rotation of the whole arm chain about the shoulder
        sh = bones["J_Bip_%s_UpperArm" % side.upper()].copy(); R = Ry(sg * arm_drop)
        for s in srcs:
            w = (s["W"] @ armB[side])[:, None]; s["V"] = s["V"] * (1 - w) + ((s["V"] - sh) @ R.T + sh) * w; wl = w[s["lv"]]; s["nr"] = s["nr"] * (1 - wl) + (s["nr"] @ R.T) * wl
        for n in list(bones):
            if armB[side][bi[n]] == 1.0 and not n.endswith("UpperArm"): bones[n] = (bones[n] - sh) @ R.T + sh
    for s in srcs: s["nr"] /= np.linalg.norm(s["nr"], axis=1, keepdims=True) + 1e-9
    B = lambda n: bones[n]; hipz = B("J_Bip_C_Hips")[2]
    piv = dict(torso=B("J_Bip_C_Spine"), head=B("J_Bip_C_Neck"), cloak=(B("J_Bip_C_UpperChest") + B("J_Bip_C_Neck")) / 2, weapon_r=B("J_Bip_R_Hand"), tail=B("J_Bip_C_Hips"))
    for s in "lr": piv.update({"arm_" + s: B("J_Bip_%s_UpperArm" % s.upper()), "forearm_" + s: B("J_Bip_%s_LowerArm" % s.upper()), "leg_" + s: B("J_Bip_%s_UpperLeg" % s.upper()), "shin_" + s: B("J_Bip_%s_LowerLeg" % s.upper())})
    ch = Char(); ch.mask = {name + '_' + sn for mn, (sn, png, mk) in mats.items() if mk}; ch.pivots = piv; ch.bones = bones; ch.k = k; ch.verts = []; ch.name = name; ch.height = height; objs = []
    bmat = {mn: make_mat(name + "_" + sn, png, mk, rough) for mn, (sn, png, mk) in mats.items()}
    for s in srcs:
        P = s["W"] @ B2P; sk = (s["W"] @ skirtB)
        if skirt_leg > 0 and (sk > .3).any():   # skirts/coats follow the legs below the hips so strides never poke through the cloth
            sw = np.clip(sk, 0, 1); lo = s["V"][:, 2][sw > .3].min()
            kk = np.clip((hipz - s["V"][:, 2]) / max(hipz - lo, .05), 0, 1) * skirt_leg * sw; gl = 1 / (1 + np.exp(-(s["V"][:, 0]) / .045))
            P = P * (1 - kk[:, None]); P[:, parts.index("leg_l")] += kk * gl; P[:, parts.index("leg_r")] += kk * (1 - gl)
        P[P.sum(1) < 1e-6, parts.index("torso")] = 1; P /= P.sum(1, keepdims=True); ix = np.argsort(-P, 1)[:, :2]; r = np.arange(len(P))
        w0, w1 = P[r, ix[:, 0]], P[r, ix[:, 1]]; wb = np.where(w1 > .03, w1 / (w0 + w1), 0.); j0 = np.array([PID[parts[i]] for i in ix[:, 0]]); j1 = np.array([PID[parts[i]] for i in ix[:, 1]])
        s["j0"], s["j1"], s["wb"] = j0, j1, np.minimum(wb, .99); ch.verts.append(s)
        tp = j0[s["tv"]]; maj = np.where(tp[:, 1] == tp[:, 2], tp[:, 1], tp[:, 0])
        for mi, mn in enumerate(s["mn"]):
            for pid in np.unique(maj[s["tm"] == mi]):
                sel = np.where((s["tm"] == mi) & (maj == pid))[0]; uv_ = np.unique(s["tv"][sel]); remap = -np.ones(len(s["V"]), int); remap[uv_] = np.arange(len(uv_))
                pv = piv[NAMES[pid]]; me = bpy.data.meshes.new("m"); me.from_pydata((s["V"][uv_] - pv).tolist(), [], remap[s["tv"][sel]].tolist())
                me.uv_layers.new(name="UVMap").data.foreach_set("uv", s["uv"][s["tl"][sel].ravel()].ravel())
                q = me.uv_layers.new(name="skin"); a = np.stack([j0[uv_].astype(float), 1.0 - (j1[uv_] + s["wb"][uv_])], 1)   # glTF flips V: (part0, 1-v = part1+blend)
                q.data.foreach_set("uv", a[remap[s["tv"][sel]].ravel()].ravel())
                me.normals_split_custom_set(s["nr"][s["tl"][sel].ravel()].tolist()); me.materials.append(bmat[mn])
                ob = bpy.data.objects.new("%s_%s" % (NAMES[pid], mats[mn][0].replace("_", "")), me); ob.location = pv.tolist(); bpy.context.collection.objects.link(ob); objs.append(ob)
    ac.OBJS.extend(objs); return ch

def tag_rigid(ob, part):
    """Give an extra (armour/prop) object the rigid skin tag so the engine treats it as 100% of one part."""
    me = ob.data
    if "skin" in me.uv_layers: return
    q = me.uv_layers.new(name="skin")
    for l in q.data: l.uv = (PID[part], 1.0 - PID[part])

def export_char(path, ch):
    """Official bpy glTF export, then fix glTF alphaMode (opaque -> OPAQUE, hair/lash/brow cards -> MASK 0.5) in the JSON chunk."""
    import json, struct
    ac.export(path); d = open(path, "rb").read(); cl = struct.unpack("<I", d[12:16])[0]; g = json.loads(d[20:20 + cl]); rest = d[20 + cl:]
    for m in g.get("materials", []):
        if m["name"] in ch.mask: m["alphaMode"] = "MASK"; m["alphaCutoff"] = 0.5
        else: m.pop("alphaMode", None); m.pop("alphaCutoff", None)
    js = json.dumps(g, separators=(",", ":")).encode(); js += b" " * ((4 - len(js) % 4) % 4)
    out = struct.pack("<II", 0x46546C67, 2) + struct.pack("<I", 12 + 8 + len(js) + len(rest)) + struct.pack("<II", len(js), 0x4E4F534A) + js + rest
    open(path, "wb").write(out); print("PATCHED alpha", path, len(out) // 1024, "KB")

def ensure_vrm(name):
    """Download a VRoid Studio sample model (CC0 / free-use: pixiv Inc. 'VRoid sample avatars') from the public madjin/vrm-samples mirror if it is not cached."""
    import urllib.request
    p = "/tmp/vrm_src/%s.vrm" % name; os.makedirs("/tmp/vrm_src", exist_ok=True)
    if not os.path.exists(p) or os.path.getsize(p) < 1e6:
        base = "https://raw.githubusercontent.com/madjin/vrm-samples/master/vroid/"
        for sub in ("beta/", "stable/"):
            try: urllib.request.urlretrieve(base + sub + name + ".vrm", p); break
            except Exception: continue
    return p
