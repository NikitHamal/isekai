#!/usr/bin/env python3
"""QA gate: verify .glb integrity/budgets/PBR textures, render 2x2 preview sheet to docs/previews/<slug>.png."""
import sys, os, json, struct, io, numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16}; NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}

def load(path):
    d = open(path, "rb").read(); mg, ver, ln = struct.unpack("<III", d[:12]); assert mg == 0x46546C67 and ver == 2 and ln == len(d), "bad GLB header"
    cl, ct = struct.unpack("<II", d[12:20]); assert ct == 0x4E4F534A; g = json.loads(d[20:20+cl]); o = 20 + cl
    bl, bt = struct.unpack("<II", d[o:o+8]); assert bt == 0x004E4942; return g, d[o+8:o+8+bl]

def accessor(g, blob, i):
    a = g["accessors"][i]; v = g["bufferViews"][a["bufferView"]]; n = NC[a["type"]]
    return np.frombuffer(blob, CT[a["componentType"]], a["count"] * n, v["byteOffset"] + a.get("byteOffset", 0)).reshape(a["count"], n)

def image(g, blob, ti):
    v = g["bufferViews"][g["images"][g["textures"][ti]["source"]]["bufferView"]]
    return np.asarray(Image.open(io.BytesIO(blob[v["byteOffset"]:v["byteOffset"] + v["byteLength"]])).convert("RGB"), float) / 255

def qmat(q):
    x, y, z, w = q; return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])

def flatten(g, blob):
    out = []
    def walk(i, M):
        n = g["nodes"][i]; L = np.eye(4); s = n.get("scale", [1, 1, 1]); L[:3, :3] = qmat(n.get("rotation", [0, 0, 0, 1])) * np.array(s); L[:3, 3] = n.get("translation", [0, 0, 0]); W = M @ L
        if "mesh" in n:
            for p in g["meshes"][n["mesh"]]["primitives"]:
                at = p["attributes"]; V = accessor(g, blob, at["POSITION"]).astype(float); N = accessor(g, blob, at["NORMAL"]).astype(float)
                out.append(dict(V=V @ W[:3, :3].T + W[:3, 3], N=N @ np.linalg.inv(W[:3, :3]), UV=accessor(g, blob, at["TEXCOORD_0"]).astype(float),
                                F=accessor(g, blob, p["indices"]).reshape(-1, 3).astype(int), mat=p["material"], T=accessor(g, blob, at["TANGENT"]).astype(float) if "TANGENT" in at else None, name=n.get("name", "")))
        for c in n.get("children", []): walk(c, W)
    for r in g["scenes"][0]["nodes"]: walk(r, np.eye(4))
    return out

def render(prims, g, blob, mode, yaw, pitch, S=512):
    tex = {}; allv = np.vstack([p["V"] for p in prims]); c = (allv.min(0) + allv.max(0)) / 2; rad = np.linalg.norm(allv.max(0) - allv.min(0)) / 2 + 1e-6
    cy, sy, cp, sp = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch)
    R = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    K = 2; im = Image.new("RGB", (S*K, S*K), (30, 34, 44) if mode != "wire" else (16, 18, 24)); dr = ImageDraw.Draw(im); polys = []
    L = np.array([.5, .8, .6]); L /= np.linalg.norm(L)
    for p in prims:
        P = (p["V"] - c) @ R.T / rad; N = p["N"] @ R.T; m = g["materials"][p["mat"]]
        if p["mat"] not in tex:
            pb = m["pbrMetallicRoughness"]; tex[p["mat"]] = (image(g, blob, pb["baseColorTexture"]["index"]), image(g, blob, m["normalTexture"]["index"]), image(g, blob, m["emissiveTexture"]["index"]) if "emissiveTexture" in m else None)
        A, NM, EM = tex[p["mat"]]; F = p["F"]; z = P[F, 2].mean(1); uv = p["UV"][F].mean(1)
        fn = N[F].mean(1); fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-9; h, w = A.shape[:2]; ix = (uv[:, 0] % 1 * (w-1)).astype(int); iy = (uv[:, 1] % 1 * (h-1)).astype(int)
        smp = lambda T_: T_[(uv[:, 1] % 1 * (T_.shape[0] - 1)).astype(int), (uv[:, 0] % 1 * (T_.shape[1] - 1)).astype(int)]; alb = A[iy, ix]; nm = smp(NM) * 2 - 1
        if p["T"] is not None and mode != "wire":
            T = p["T"][F][:, :, :3].mean(1) @ R.T; T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-9; B = np.cross(fn, T); fn2 = T * nm[:, :1] + B * nm[:, 1:2] + fn * nm[:, 2:3]; fn2 /= np.linalg.norm(fn2, axis=1, keepdims=True) + 1e-9
        else: fn2 = fn
        dif = np.clip(fn2 @ L, 0, 1)[:, None]; col = alb * (.25 + .85 * dif)
        if EM is not None: col = col + smp(EM) * .8
        if mode == "normal": col = fn2 * .5 + .5
        col = (np.clip(col, 0, 1) * 255).astype(np.uint8)
        for k in np.where(fn[:, 2] > -0.0 if mode != "wire" else fn[:, 2] > -2)[0]: polys.append((z[k], P[F[k], :2], col[k]))
    polys.sort(key=lambda t: t[0])
    for z, q, col in polys:
        pts = [((x * .6 + .5) * S*K, (.52 - y * .6) * S*K) for x, y in q]
        if mode == "wire": dr.polygon(pts, outline=(90, 200, 160))
        else: dr.polygon(pts, fill=tuple(int(x) for x in col))
    return im.resize((S, S), Image.LANCZOS)

def main(path):
    slug = os.path.splitext(os.path.basename(path))[0]; g, blob = load(path); prims = flatten(g, blob); errs = []
    tris = sum(len(p["F"]) for p in prims); budgets = json.load(open(os.path.join(HERE, "asset_budgets.json"))); need = budgets.get(slug, {}).get("min_tris", 3000)
    if tris < need: errs.append(f"triangles {tris} < {need}")
    for m in g["materials"]:
        pb = m["pbrMetallicRoughness"]
        for k, t in (("baseColor", pb.get("baseColorTexture")), ("metallicRoughness", pb.get("metallicRoughnessTexture")), ("normal", m.get("normalTexture"))):
            if t is None: errs.append(f"{m['name']}: missing {k} texture")
    for p in prims:
        if not np.isfinite(p["V"]).all() or not np.isfinite(p["N"]).all(): errs.append("non-finite data")
        if p["F"].max() >= len(p["V"]): errs.append("index OOB")
        if len(p["UV"]) != len(p["V"]) or p["UV"].std() == 0: errs.append("bad UV")
    sheet = Image.new("RGB", (1024, 1024)); views = [("shaded", -.5, .25), ("shaded", 1.2, .2), ("normal", 2.6, .3), ("wire", .5, .35)]
    for i, (md, yw, pt) in enumerate(views): sheet.paste(render(prims, g, blob, md, yw, pt), ((i % 2) * 512, (i // 2) * 512))
    os.makedirs(os.path.join(ROOT, "docs/previews"), exist_ok=True); prev = os.path.join(ROOT, "docs/previews", slug + ".png"); sheet.save(prev, optimize=True)
    print(f"{'FAIL' if errs else 'PASS'} {slug}: tris={tris} (min {need}) materials={len(g['materials'])} nodes={len(g['nodes'])} size={os.path.getsize(path)//1024}KB preview={os.path.relpath(prev, ROOT)}")
    for e in errs: print("  -", e)
    return 1 if errs else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1]))
