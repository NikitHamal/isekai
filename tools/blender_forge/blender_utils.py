#!/usr/bin/env python3
"""Real Headless Blender (bpy + bmesh + Modifiers + Smart UV + glTF 2.0 Export) pipeline for Chronicles of Aetheria."""
import os, sys, math, tempfile
import numpy as np
import bpy, bmesh, mathutils

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
ASSETS_DIR = os.path.join(TOOLS_DIR, "assets")
ROOT_DIR = os.path.dirname(TOOLS_DIR)
for p in (TOOLS_DIR, ASSETS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from vork_forge import pbr_shader
from kingdom_lib import *

_MAT_CACHE = {}
_TMP_DIR = tempfile.mkdtemp(prefix="isekai_bpy_tex_")

def reset_blender_scene():
    """Reset Blender to a clean empty factory scene."""
    _MAT_CACHE.clear()
    bpy.ops.wm.read_factory_settings(use_empty=True)

def gltf_to_blender_vec(v):
    """Convert glTF Y-up (+Z forward) coordinate (x, y, z) to Blender Z-up (-Y forward) (x, -z, y)."""
    return (float(v[0]), float(-v[2]), float(v[1]))

def make_blender_pbr_material(mat_spec, tex_size=512):
    """Build a Blender Principled BSDF material with BaseColor, NormalMap, MetallicRoughness & Emissive textures."""
    key = (mat_spec.name, tex_size)
    if key in _MAT_CACHE:
        return _MAT_CACHE[key]
    baked = pbr_shader.bake(mat_spec, n=tex_size)
    bmat = bpy.data.materials.new(name=mat_spec.name)
    bmat.use_backface_culling = False
    nt = bmat.node_tree
    nt.nodes.clear()
    out_node = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

    def _load_png_bytes(suffix, png_bytes, non_color=False):
        fpath = os.path.join(_TMP_DIR, f"{mat_spec.name}_{tex_size}_{suffix}.png")
        with open(fpath, "wb") as f:
            f.write(png_bytes)
        img = bpy.data.images.load(fpath, check_existing=True)
        if non_color:
            img.colorspace_settings.name = "Non-Color"
        return img

    # 1. Base Color
    tex_bc = nt.nodes.new("ShaderNodeTexImage")
    tex_bc.image = _load_png_bytes("bc", baked["albedo"], non_color=False)
    nt.links.new(tex_bc.outputs["Color"], bsdf.inputs["Base Color"])

    # 2. Metallic-Roughness (glTF convention: G = Roughness, B = Metallic)
    tex_mr = nt.nodes.new("ShaderNodeTexImage")
    tex_mr.image = _load_png_bytes("mr", baked["mr"], non_color=True)
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(tex_mr.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])

    # 3. Tangent-Space Normal Map
    tex_nm = nt.nodes.new("ShaderNodeTexImage")
    tex_nm.image = _load_png_bytes("nm", baked["normal"], non_color=True)
    nm_node = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(tex_nm.outputs["Color"], nm_node.inputs["Color"])
    nt.links.new(nm_node.outputs["Normal"], bsdf.inputs["Normal"])

    # 4. Optional Emissive Map
    if baked.get("emissive") is not None:
        tex_em = nt.nodes.new("ShaderNodeTexImage")
        tex_em.image = _load_png_bytes("em", baked["emissive"], non_color=False)
        nt.links.new(tex_em.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 1.0

    _MAT_CACHE[key] = bmat
    return bmat

def apply_modifier_stack(obj, modifiers):
    """Attach and apply a list of Blender modifiers [(kind, params_dict), ...] to obj."""
    if not modifiers:
        return
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for idx, (kind, params) in enumerate(modifiers):
        mname = f"{kind}_{idx}"
        if kind == "SUBSURF":
            mod = obj.modifiers.new(mname, 'SUBSURF')
            mod.levels = params.get("levels", 1)
            mod.subdivision_type = params.get("type", 'CATMULL_CLARK')
        elif kind == "BEVEL":
            mod = obj.modifiers.new(mname, 'BEVEL')
            mod.width = params.get("width", 0.018)
            mod.segments = params.get("segments", 2)
            mod.limit_method = params.get("limit_method", 'ANGLE')
            mod.angle_limit = params.get("angle_limit", 0.55)
        elif kind == "SOLIDIFY":
            mod = obj.modifiers.new(mname, 'SOLIDIFY')
            mod.thickness = params.get("thickness", 0.025)
            mod.offset = params.get("offset", 0.0)
        elif kind == "DISPLACE":
            tex_type = params.get("tex_type", 'VORONOI')
            tex = bpy.data.textures.new(f"DispTex_{obj.name}_{idx}", type=tex_type)
            if hasattr(tex, "noise_scale"):
                tex.noise_scale = params.get("scale", 0.65)
            mod = obj.modifiers.new(mname, 'DISPLACE')
            mod.texture = tex
            mod.strength = params.get("strength", 0.14)
            mod.mid_level = params.get("mid_level", 0.5)
        elif kind == "MIRROR":
            mod = obj.modifiers.new(mname, 'MIRROR')
            mod.use_axis[0] = params.get("axis_x", True)
            mod.use_axis[1] = params.get("axis_y", False)
            mod.use_axis[2] = params.get("axis_z", False)
            mod.use_clip = params.get("use_clip", True)
        elif kind == "ARRAY":
            mod = obj.modifiers.new(mname, 'ARRAY')
            mod.count = params.get("count", 4)
            mod.use_relative_offset = params.get("relative", False)
            mod.use_constant_offset = not mod.use_relative_offset
            off = params.get("offset", (1.0, 0.0, 0.0))
            if mod.use_constant_offset:
                mod.constant_offset_displace = gltf_to_blender_vec(off)
            else:
                mod.relative_offset_displace = off
        bpy.ops.object.modifier_apply(modifier=mname)

def smart_uv_unwrap(obj, angle_limit=1.15, island_margin=0.02, uv_scale=1.0):
    """Unwrap obj using Blender's Smart UV Project and optional UV scaling."""
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=angle_limit, island_margin=island_margin)
    bpy.ops.object.mode_set(mode='OBJECT')
    if abs(uv_scale - 1.0) > 1e-4 and obj.data.uv_layers.active:
        uv_data = obj.data.uv_layers.active.data
        for l in uv_data:
            l.uv[0] *= uv_scale
            l.uv[1] *= uv_scale

def finalize_blender_object(obj, mat_spec, modifiers=(), smart_uv=False, uv_scale=1.0, pivot_gltf=None, tex_size=512):
    """Apply modifiers, optional Smart UV Project, triangulate, smooth normals, set joint origin, and assign PBR material."""
    apply_modifier_stack(obj, modifiers)
    if smart_uv or not obj.data.uv_layers:
        smart_uv_unwrap(obj, uv_scale=uv_scale)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if pivot_gltf is not None:
        pb = mathutils.Vector(gltf_to_blender_vec(pivot_gltf))
        obj.data.transform(mathutils.Matrix.Translation(-pb))
        obj.location = pb
    bmat = make_blender_pbr_material(mat_spec, tex_size=tex_size)
    obj.data.materials.clear()
    obj.data.materials.append(bmat)
    return obj

def add_bmesh_object(name, bm, mat_spec, modifiers=(), smart_uv=True, uv_scale=1.5, pivot_gltf=None, tex_size=512, is_gltf_coords=True):
    """Create a Blender Object from a BMesh, apply Blender modifiers, Smart UV unwrap, and assign PBR material."""
    if is_gltf_coords:
        for v in bm.verts:
            x, y, z = v.co.x, v.co.y, v.co.z
            v.co = (x, -z, y)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finalize_blender_object(
        obj, mat_spec, modifiers=modifiers, smart_uv=smart_uv, uv_scale=uv_scale, pivot_gltf=pivot_gltf, tex_size=tex_size
    )

def add_mesh_object(name, m, mat_spec, modifiers=(), smart_uv=False, weld_dist=1e-4, pivot_gltf=None, tex_size=512):
    """Convert Mesh(V, F, UV) into a real Blender Object via BMesh, weld vertices, apply Blender modifiers, and assign PBR."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    verts = [bm.verts.new(gltf_to_blender_vec(v)) for v in m.V]
    bm.verts.ensure_lookup_table()
    for f in m.F:
        i0, i1, i2 = int(f[0]), int(f[1]), int(f[2])
        if i0 == i1 or i1 == i2 or i0 == i2:
            continue
        try:
            face = bm.faces.new((verts[i0], verts[i1], verts[i2]))
            for loop, vi in zip(face.loops, (i0, i1, i2)):
                loop[uv_layer].uv = (float(m.UV[vi, 0]), float(1.0 - m.UV[vi, 1]))
        except ValueError:
            pass
    if weld_dist > 0 and modifiers:
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=weld_dist)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return finalize_blender_object(
        obj, mat_spec, modifiers=modifiers, smart_uv=smart_uv, uv_scale=1.0, pivot_gltf=pivot_gltf, tex_size=tex_size
    )

def export_blender_scene(out_path):
    """Export the active Blender scene to GLB via official bpy.ops.export_scene.gltf."""
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format='GLB',
        export_yup=True,
        export_apply=False,
        export_texcoords=True,
        export_normals=True,
        export_tangents=True
    )
    return out_path

def export_blender_glb(root_node, out_path, tex_size=512, node_modifiers=None, part_pivots=None):
    """Build all nodes of root_node in headless Blender with modifiers & pivots and export via bpy.ops.export_scene.gltf."""
    reset_blender_scene()
    node_modifiers = node_modifiers or {}
    part_pivots = part_pivots or {}

    def _walk(n):
        if n.mesh is not None and n.material is not None:
            mods = node_modifiers.get(n.name, ())
            piv = part_pivots.get(n.name, None)
            if piv is None:
                for prefix, pval in part_pivots.items():
                    if n.name.startswith(prefix):
                        piv = pval
                        break
            add_mesh_object(n.name, n.mesh, n.material, modifiers=mods, pivot_gltf=piv, tex_size=tex_size)
        for ch in n.children:
            _walk(ch)

    _walk(root_node)
    return export_blender_scene(out_path)

def export_articulated_character_glb(root_node, out_path, tex_size=512, is_quadruped=False, node_modifiers=None):
    """Build an articulated character/monster in Blender with separate named limb objects & joint origins and export to GLB."""
    reset_blender_scene()
    node_modifiers = node_modifiers or {}
    flat_nodes = []
    def _collect(n):
        if n.mesh is not None and n.material is not None and len(n.mesh.F) > 0:
            flat_nodes.append(n)
        for ch in n.children:
            _collect(ch)
    _collect(root_node)

    all_v = np.vstack([n.mesh.V for n in flat_nodes])
    bmin = all_v.min(axis=0)
    bmax = all_v.max(axis=0)
    H = max(float(bmax[1] - bmin[1]), 0.01)
    W = max(float(bmax[0] - bmin[0]), 0.01)
    L = max(float(bmax[2] - bmin[2]), 0.01)
    zc = 0.5 * float(bmin[2] + bmax[2])

    wpn_keys = ("sword", "blade", "grip", "runes", "axe", "cleaver", "hammer", "staff", "bow", "dagger", "halberd", "crossbow")
    wx_vals = [n.mesh.V[:, 0].mean() for n in flat_nodes if any(k in n.name for k in wpn_keys)]
    w_side = (1.0 if np.mean(wx_vals) >= 0.0 else -1.0) if wx_vals else -1.0

    def _pivot_for(part):
        if is_quadruped:
            if part == "head": return (0.0, float(bmin[1]) + 0.65 * H, zc + 0.24 * L)
            if part == "leg_l": return (0.0, float(bmin[1]) + 0.50 * H, zc + 0.24 * L)
            if part == "leg_r": return (0.0, float(bmin[1]) + 0.50 * H, zc - 0.24 * L)
            if part in ("jaw", "tail"): return (0.0, float(bmin[1]) + 0.58 * H, zc - 0.30 * L)
            return (0.0, float(bmin[1]) + 0.52 * H, zc)
        if part == "head": return (0.0, float(bmin[1]) + 0.80 * H, 0.0)
        if part == "cloak": return (0.0, float(bmin[1]) + 0.82 * H, -0.05 * L)
        if part in ("arm_r", "weapon_r"): return (w_side * 0.19 * W, float(bmin[1]) + 0.76 * H, 0.0)
        if part == "arm_l": return (-w_side * 0.19 * W, float(bmin[1]) + 0.76 * H, 0.0)
        if part == "leg_l": return (0.08 * W, float(bmin[1]) + 0.46 * H, 0.0)
        if part == "leg_r": return (-0.08 * W, float(bmin[1]) + 0.46 * H, 0.0)
        return (0.0, float(bmin[1]) + 0.46 * H, 0.0)

    for n in flat_nodes:
        nm = n.name.lower()
        mods = node_modifiers.get(n.name, ())
        fixed = None
        for pfx in ("torso", "head", "cloak", "arm_l", "arm_r", "leg_l", "leg_r", "weapon_r", "jaw", "tail"):
            if nm.startswith(pfx + "_") or nm == pfx:
                fixed = pfx
                break
        if fixed is None:
            if any(k in nm for k in ("cloak", "cape", "lining")): fixed = "cloak"
            elif any(k in nm for k in wpn_keys): fixed = "weapon_r"
            elif any(k in nm for k in ("buckler", "shield", "glyph", "quiver")): fixed = "arm_l"
            elif any(k in nm for k in ("hair", "eyes", "helm", "visor", "crest", "plume", "horns", "tusks", "ears", "hat", "hood")): fixed = "head"
        if fixed is not None:
            obj_name = n.name if n.name.startswith(fixed) else f"{fixed}_{n.name}"
            add_mesh_object(obj_name, n.mesh, n.material, modifiers=mods, pivot_gltf=_pivot_for(fixed), tex_size=tex_size)
            continue

        # Partition multi-limb body/armor mesh into anatomical Blender limb sub-objects
        V, F, UV = n.mesh.V, n.mesh.F, n.mesh.UV
        fc = V[F].mean(axis=1)
        ny = (fc[:, 1] - bmin[1]) / H
        nz = (fc[:, 2] - zc) / L
        parts_map = {}
        for fi in range(len(F)):
            if is_quadruped:
                if nz[fi] < -0.28: p = "tail"
                elif ny[fi] < 0.48: p = "leg_l" if nz[fi] >= 0.0 else "leg_r"
                elif nz[fi] > 0.25: p = "head"
                else: p = "torso"
            else:
                if ny[fi] < 0.45: p = "leg_l" if fc[fi, 0] >= 0.0 else "leg_r"
                elif ny[fi] >= 0.81: p = "head"
                elif abs(fc[fi, 0]) > 0.20 * W: p = "arm_r" if (fc[fi, 0] * w_side > 0.0) else "arm_l"
                else: p = "torso"
            parts_map.setdefault(p, []).append(fi)

        for p, f_indices in parts_map.items():
            sub_F = F[np.array(f_indices, dtype=np.int64)]
            used = np.unique(sub_F)
            remap = np.zeros(len(V), dtype=np.int64)
            remap[used] = np.arange(len(used))
            sub_mesh = Mesh(V[used], remap[sub_F], UV[used])
            add_mesh_object(f"{p}_{n.name}", sub_mesh, n.material, modifiers=mods, pivot_gltf=_pivot_for(p), tex_size=tex_size)

    return export_blender_scene(out_path)

def load_asset_root(mod_name):
    """Import an asset module from tools/assets/ and return its root Node."""
    m = __import__(f"assets.{mod_name}", fromlist=["*"])
    return getattr(m, "root_node", None) or getattr(m, "root")

def cone(r, h, pos=(0, 0, 0), sides=12, rot=(0, 0, 0), d=0.8):
    """Tapered cone mesh helper."""
    return cyl_tri(r, h, pos, d=d, sides=sides, r2=0.002, rot=rot)
