#!/usr/bin/env python3
"""Blender (bpy + bmesh + BEVEL + SUBSURF + DISPLACE) generator for bld_apothecary_magic_tower.glb."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *

COPPER_DOME = Material("verdigris_copper_dome", "hammered_metal", (.22, .56, .48), (.12, .32, .26), rough=.42, metal=.82, scale=8, bump=2.5, seed=191)
AETHER_CRYSTAL = Material("arcane_spire_crystal", "runic_glow", (.25, .82, 1.0), (.10, .45, .85), rough=.15, emissive=(.30, .85, 1.0), scale=5, seed=192)

# 1. Stepped octagonal stone base plinth & buttresses
plinth_parts = [
    cyl_tri(3.9, 0.55, (0.0, 0.275, 0.0), d=0.35, sides=16),
    cyl_tri(3.5, 0.45, (0.0, 0.72, 0.0), d=0.35, sides=16),
    box_tri((2.2, 0.50, 1.6), (0.0, 0.25, 3.8), d=0.4),
]
for i in range(8):
    a = i * 2 * np.pi / 8 + np.pi / 8
    ca, sa = np.cos(a), np.sin(a)
    plinth_parts.append(box_tri((0.65, 3.8, 0.85), (ca * 3.15, 2.3, sa * 3.15), rot=(0, -np.degrees(a), 0), d=0.45))

# 2. Cylindrical masonry tower shaft + arched entrance & stone courses
tower_stone = merge([
    round_tower(2.95, 7.6, (0.0, 0.85, 0.0), seed=41, battlements=False),
    arch_opening(0.0, 0.85, 1.6, 1.8, 2.98, 0.52, n=13),
])

# 3. Cantilevered timber-and-plaster alchemical upper gallery (y = 7.8 to 10.6)
gallery_plaster = cyl_tri(3.35, 2.6, (0.0, 9.1, 0.0), d=0.4, sides=16, rings=2)
timber_ribs = []
for i in range(16):
    a = i * 2 * np.pi / 16
    ca, sa = np.cos(a), np.sin(a)
    timber_ribs += [
        box_tri((0.20, 2.7, 0.22), (ca * 3.38, 9.1, sa * 3.38), rot=(0, -np.degrees(a), 0), d=0.6),
        beam((ca * 2.85, 7.2, sa * 2.85), (ca * 3.45, 7.85, sa * 3.45), 0.18),
    ]

# 4. Ribbed verdigris-copper astronomical observatory dome + golden armillary rings
dome_parts = [
    ell((0.0, 10.5, 0.0), (3.45, 2.85, 3.45), rings=18, sides=28),
    cyl_tri(0.85, 1.2, (0.0, 13.1, 0.0), d=0.6, sides=20, r2=0.45),
]
gold_rings = [
    cyl_tri(3.52, 0.22, (0.0, 10.45, 0.0), d=0.8, sides=28),
    cyl_tri(1.35, 0.09, (0.0, 14.3, 0.0), d=0.8, sides=24, rot=(32, 0, 18)),
    cyl_tri(1.15, 0.09, (0.0, 14.3, 0.0), d=0.8, sides=24, rot=(-28, 45, -20)),
    tube((0.0, 13.4, 0.0), (0.0, 15.6, 0.0), 0.08, sides=14, r2=0.02),
]
for i in range(8):
    a = i * np.pi / 8
    gold_rings.append(ell((0.0, 10.5, 0.0), (3.49, 2.89, 0.14), rings=14, sides=18, rot=(0, np.degrees(a), 0)))

# 5. Floating Aether Crystal beacon & warm/arcane lit arched windows
crystal_parts = [
    cone(0.45, 1.15, (0.0, 14.6, 0.0), sides=8),
    cone(0.45, 0.75, (0.0, 13.9, 0.0), sides=8, rot=(180, 0, 0)),
]
for i in range(6):
    a = i * 2 * np.pi / 6
    crystal_parts.append(ell((np.cos(a) * 3.42, 9.1, np.sin(a) * 3.42), (0.28, 0.55, 0.28), rings=8, sides=12))

warm_windows = []
for i in range(6):
    a = i * 2 * np.pi / 6 + 0.52
    warm_windows.append(box_tri((0.65, 1.15, 0.16), (np.cos(a) * 2.98, 4.8, np.sin(a) * 2.98), rot=(0, -np.degrees(a), 0), d=0.5))

door_wood = box_tri((1.4, 2.1, 0.18), (0.0, 1.85, 2.96), d=0.8)

root_node = node("bld_apothecary_magic_tower", children=[
    node("octagonal_plinth_buttresses", merge(plinth_parts), DARKSTONE),
    node("tower_masonry_shaft", tower_stone, CASTLE),
    node("alchemical_gallery_plaster", gallery_plaster, PLASTER),
    node("gallery_oak_timbers", merge(timber_ribs), BEAM),
    node("copper_observatory_dome", merge(dome_parts), COPPER_DOME),
    node("golden_armillary_ribs", merge(gold_rings), GOLDM),
    node("arcane_crystal_spire", merge(crystal_parts), AETHER_CRYSTAL),
    node("warm_leaded_windows", merge(warm_windows), GLASSLIT),
    node("oak_arch_door", door_wood, OAKP),
])

if __name__ == "__main__":
    p = export_blender_glb(
        root_node,
        out("buildings", "bld_apothecary_magic_tower"),
        tex_size=512,
        node_modifiers={
            "octagonal_plinth_buttresses": [("BEVEL", {"width": 0.025, "segments": 1})],
            "arcane_crystal_spire": [("BEVEL", {"width": 0.015, "segments": 1})],
        }
    )
    print("Blender exported:", p)
