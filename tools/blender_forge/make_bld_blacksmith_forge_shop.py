#!/usr/bin/env python3
"""Blender (bpy + bmesh + BEVEL + DISPLACE) generator for bld_blacksmith_forge_shop.glb."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *

FORGE_COALS = Material("glowing_forge_coals", "runic_glow", (.95, .28, .05), (.35, .08, .02), rough=.45, emissive=(1.0, .42, .08), scale=6, seed=181)
BRICK_HEARTH = Material("firebrick_masonry", "cut_stone", (.58, .26, .18), (.34, .14, .09), rough=.90, scale=10, bump=4.0, seed=182)

# 1. Foundation plinth + enclosed workshop back/left walls + open front smithy bay
plinth = merge([
    box_tri((9.6, 0.45, 7.4), (0.0, 0.225, 0.0), d=0.4),
    box_tri((2.4, 0.24, 1.4), (-1.8, 0.12, 4.1), d=0.4),
])

# Hewn stone walls: enclosed left wing (x in [-4.5, 0.2]) + forge back wall
stone_walls = merge([
    block_wall(-4.5, 0.2, 0.45, 3.6, 3.3, 0.42, seed=11, holes=[(-2.6, -1.0, 0.45, 2.55)]),
    block_wall(-4.5, 4.4, 0.45, 3.6, -3.3, 0.42, seed=12, holes=[(-3.2, -1.6, 1.3, 2.5)]),
    block_wall(-3.3, 3.3, 0.45, 3.6, -4.5, 0.42, seed=13, axis=1, holes=[(-1.2, 1.2, 1.3, 2.5)]),
    block_wall(-3.3, 3.3, 0.45, 3.6, 0.2, 0.38, seed=14, axis=1),
    # Low stone dwarf wall around right-side open smithy bay (x in [0.2, 4.5])
    block_wall(0.2, 4.5, 0.45, 1.25, 3.3, 0.38, seed=15),
    block_wall(-3.3, 3.3, 0.45, 1.25, 4.5, 0.38, seed=16, axis=1),
])

# 2. Massive stone & firebrick forge furnace, arched hood, and tall chimney stack on right rear
forge_masonry = merge([
    box_tri((2.6, 1.4, 2.2), (2.5, 1.15, -2.0), d=0.45),
    arch_opening(2.5, 1.15, 1.5, 0.85, -0.88, 0.48, n=11),
    box_tri((2.3, 1.3, 1.8), (2.5, 2.45, -2.1), d=0.45),
    box_tri((1.5, 4.2, 1.4), (2.5, 5.1, -2.2), d=0.45),
    box_tri((1.75, 0.28, 1.65), (2.5, 7.25, -2.2), d=0.45),
])

coals_mesh = merge([
    ell((2.5 + (i - 1.5) * 0.26, 1.32, -1.65 + (j - 1) * 0.22), (0.24, 0.12, 0.22), rings=8, sides=12)
    for i in range(4) for j in range(3)
])

# 3. Upper half-timbered gable wall & heavy oak post-and-beam smithy structure
plaster_upper = merge([
    poly_prism([(-4.5, 3.6), (0.2, 3.6), (-2.15, 6.2)], 0.36, (0.0, 0.0, 3.25)),
    poly_prism([(-4.5, 3.6), (0.2, 3.6), (-2.15, 6.2)], 0.36, (0.0, 0.0, -3.25)),
])

beams = []
for x in (-4.4, -2.15, 0.1, 2.3, 4.4):
    for z in (-3.2, 3.2):
        beams.append(box_tri((0.24, 3.2, 0.24), (x, 2.05, z), d=0.6))
        if x > 0.0:
            beams.append(beam((x, 2.6, z), (x - 0.55, 3.45, z), 0.16))
            beams.append(beam((x, 2.6, z), (x, 3.45, z - np.sign(z) * 0.55), 0.16))
for z in (-3.25, 3.25):
    beams += [
        box_tri((9.2, 0.24, 0.26), (0.0, 3.55, z), d=0.6),
        beam((-4.5, 3.6, z), (-2.15, 6.2, z), 0.22),
        beam((0.2, 3.6, z), (-2.15, 6.2, z), 0.22),
    ]

# 4. Steep slate gable roof over main hall + pitched porch roof over open smithy bay
slate_main, ridge_main = gable_roof(6.8, 2.55, 2.65, (0.0, 0.0, 0.0), over=0.45, lip_rows=10)
slate_main = slate_main.tf((-2.15, 3.55, 0.0), (0, 90, 0))
ridge_main = ridge_main.tf((-2.15, 3.55, 0.0), (0, 90, 0))
slate_bay, ridge_bay = gable_roof(4.6, 3.4, 1.65, (2.35, 3.45, 0.0), over=0.40, lip_rows=8)

# 5. Blacksmith Anvil on oak stump, quench barrel, weapon rack & glowing windows
anvil_stump = cyl_tri(0.42, 0.65, (1.8, 0.78, 0.8), d=0.8, sides=18)
anvil_steel = merge([
    box_tri((0.68, 0.22, 0.36), (1.8, 1.20, 0.8), d=1.2),
    box_tri((0.52, 0.26, 0.28), (1.8, 1.42, 0.8), d=1.2),
    cone(0.14, 0.42, (2.22, 1.44, 0.8), sides=14, rot=(0, 0, -90)),
    # Forged glowing-hot blade on the anvil + weapon rack blades
    box_tri((0.08, 0.02, 0.85), (1.8, 1.57, 0.8), rot=(0, 25, 0), d=1.5),
])

quench_barrel = merge([
    cyl_tri(0.36, 0.78, (0.9, 0.84, 1.6), d=0.9, sides=18, r2=0.33),
    box_tri((1.3, 0.95, 0.12), (-1.8, 1.42, 3.32), d=0.8),
])

lit_windows = merge([
    box_tri((1.1, 1.0, 0.08), (-2.4, 1.9, -3.32), d=0.5),
    box_tri((0.08, 1.0, 1.4), (-4.52, 1.9, 0.0), d=0.5),
])

root_node = node("bld_blacksmith_forge_shop", children=[
    node("foundation_plinth", plinth, DARKSTONE),
    node("smithy_stone_walls", stone_walls, CASTLE),
    node("forge_chimney_hearth", forge_masonry, BRICK_HEARTH),
    node("glowing_forge_coals", coals_mesh, FORGE_COALS),
    node("upper_plaster_gables", plaster_upper, PLASTER),
    node("oak_timber_frame", merge(beams), BEAM),
    node("slate_roof_shingles", merge([slate_main, slate_bay]), SLATE),
    node("roof_ridge_stone", merge([ridge_main, ridge_bay]), STONEF),
    node("oak_stump_and_door", merge([anvil_stump, quench_barrel]), OAKP),
    node("steel_anvil_and_blades", anvil_steel, DAMASK),
    node("lit_workshop_windows", lit_windows, GLASSLIT),
])

if __name__ == "__main__":
    p = export_blender_glb(
        root_node,
        out("buildings", "bld_blacksmith_forge_shop"),
        tex_size=512,
        node_modifiers={
            "foundation_plinth": [("BEVEL", {"width": 0.025, "segments": 2})],
            "forge_chimney_hearth": [("BEVEL", {"width": 0.02, "segments": 1})],
            "steel_anvil_and_blades": [("BEVEL", {"width": 0.012, "segments": 2})],
            "glowing_forge_coals": [("SUBSURF", {"levels": 1}), ("DISPLACE", {"tex_type": "VORONOI", "strength": 0.03, "scale": 0.6})],
        }
    )
    print("Blender exported:", p)
