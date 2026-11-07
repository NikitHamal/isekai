"""Compile a vork_forge node hierarchy into spec-compliant binary glTF 2.0 (.glb) with embedded PBR textures."""
import json, struct, os, numpy as np
from .dsl import Node, _rot
from .pbr_shader import bake

def _quat(rot):
    R = _rot(rot); t = np.trace(R)
    if t > 0: s = np.sqrt(t + 1) * 2; q = [(R[2,1]-R[1,2])/s, (R[0,2]-R[2,0])/s, (R[1,0]-R[0,1])/s, s/4]
    elif R[0,0] > R[1,1] and R[0,0] > R[2,2]: s = np.sqrt(1+R[0,0]-R[1,1]-R[2,2])*2; q = [s/4, (R[0,1]+R[1,0])/s, (R[0,2]+R[2,0])/s, (R[2,1]-R[1,2])/s]
    elif R[1,1] > R[2,2]: s = np.sqrt(1+R[1,1]-R[0,0]-R[2,2])*2; q = [(R[0,1]+R[1,0])/s, s/4, (R[1,2]+R[2,1])/s, (R[0,2]-R[2,0])/s]
    else: s = np.sqrt(1+R[2,2]-R[0,0]-R[1,1])*2; q = [(R[0,2]+R[2,0])/s, (R[1,2]+R[2,1])/s, s/4, (R[1,0]-R[0,1])/s]
    q = np.array(q); return (q / np.linalg.norm(q)).tolist()

def tangents(V, N, UV, F):
    e1 = V[F[:,1]] - V[F[:,0]]; e2 = V[F[:,2]] - V[F[:,0]]; d1 = UV[F[:,1]] - UV[F[:,0]]; d2 = UV[F[:,2]] - UV[F[:,0]]
    det = d1[:,0]*d2[:,1] - d2[:,0]*d1[:,1]; det[np.abs(det) < 1e-12] = 1e-12; r = 1.0 / det
    t = (e1 * d2[:,1:2] - e2 * d1[:,1:2]) * r[:,None]; T = np.zeros_like(V)
    for i in range(3): np.add.at(T, F[:,i], t)
    T = T - N * (T * N).sum(1, keepdims=True); l = np.linalg.norm(T, axis=1, keepdims=True)
    fb = np.cross(N, [0.3, 1, 0.2]); T = np.where(l > 1e-9, T / np.maximum(l, 1e-9), fb / (np.linalg.norm(fb, axis=1, keepdims=True) + 1e-9))
    return np.hstack([T, np.ones((len(V), 1))]).astype(np.float32)

def compile_glb(root, path, tex_size=512):
    nodes_json, meshes, mats, mat_idx, bv, acc, images, textures = [], [], [], {}, [], [], [], []
    blob = bytearray()
    def add_bv(data, target=None):
        while len(blob) % 4: blob.append(0)
        d = {"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)}
        if target: d["target"] = target
        blob.extend(data); bv.append(d); return len(bv) - 1
    def add_acc(arr, ctype, target, minmax=False):
        arr = np.ascontiguousarray(arr); comp = 5126 if arr.dtype == np.float32 else 5125
        a = {"bufferView": add_bv(arr.tobytes(), target), "componentType": comp, "count": len(arr), "type": ctype}
        if minmax: a["min"] = arr.min(0).tolist(); a["max"] = arr.max(0).tolist()
        acc.append(a); return len(acc) - 1
    def add_tex(png):
        images.append({"bufferView": add_bv(png), "mimeType": "image/png"}); textures.append({"source": len(images) - 1, "sampler": 0}); return len(textures) - 1
    def material(m):
        if m.name in mat_idx: return mat_idx[m.name]
        b = bake(m, tex_size); mt = {"name": m.name, "pbrMetallicRoughness": {"baseColorTexture": {"index": add_tex(b["albedo"])},
              "metallicRoughnessTexture": {"index": add_tex(b["mr"])}, "baseColorFactor": [1, 1, 1, m.alpha], "metallicFactor": 1.0, "roughnessFactor": 1.0},
              "normalTexture": {"index": add_tex(b["normal"])}, "doubleSided": True}
        if b["emissive"]: mt["emissiveTexture"] = {"index": add_tex(b["emissive"])}; mt["emissiveFactor"] = [1, 1, 1]
        if m.alpha < 1: mt["alphaMode"] = "BLEND"
        mats.append(mt); mat_idx[m.name] = len(mats) - 1; return mat_idx[m.name]
    def walk(n):
        d = {"name": n.name}
        if n.mesh is not None and n.mesh.tris:
            ms = n.mesh; V = ms.V.astype(np.float32); N = ms.normals().astype(np.float32); UV = ms.UV.astype(np.float32); F = ms.F.astype(np.uint32)
            p = {"attributes": {"POSITION": add_acc(V, "VEC3", 34962, True), "NORMAL": add_acc(N, "VEC3", 34962),
                 "TEXCOORD_0": add_acc(UV, "VEC2", 34962), "TANGENT": add_acc(tangents(V, N, UV, F.astype(np.int64)), "VEC4", 34962)},
                 "indices": add_acc(F.reshape(-1), "SCALAR", 34963), "material": material(n.material), "mode": 4}
            meshes.append({"name": n.name, "primitives": [p]}); d["mesh"] = len(meshes) - 1
        if tuple(n.pos) != (0,0,0): d["translation"] = [float(x) for x in n.pos]
        if tuple(n.rot) != (0,0,0): d["rotation"] = _quat(n.rot)
        if tuple(n.scale) != (1,1,1): d["scale"] = [float(x) for x in n.scale]
        idx = len(nodes_json); nodes_json.append(d)
        ch = [walk(c) for c in n.children]
        if ch: d["children"] = ch
        return idx
    r = walk(root)
    g = {"asset": {"version": "2.0", "generator": "vork_forge"}, "scene": 0, "scenes": [{"nodes": [r]}], "nodes": nodes_json, "meshes": meshes,
         "materials": mats, "images": images, "textures": textures, "samplers": [{"magFilter": 9729, "minFilter": 9987, "wrapS": 10497, "wrapT": 10497}],
         "bufferViews": bv, "accessors": acc, "buffers": [{"byteLength": len(blob)}]}
    js = json.dumps(g, separators=(",", ":")).encode(); js += b" " * (-len(js) % 4); blob.extend(b"\0" * (-len(blob) % 4))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob)))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js); f.write(struct.pack("<II", len(blob), 0x004E4942) + bytes(blob))
    return path
