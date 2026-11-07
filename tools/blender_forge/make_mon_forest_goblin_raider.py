#!/usr/bin/env python3
"""Blender (bpy + bmesh + SUBSURF + SOLIDIFY + BEVEL) generator for mon_forest_goblin_raider.glb."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *

GOBLIN_SKIN = Material("goblin_moss_hide", "fbm_noise", (.28, .44, .18), (.14, .24, .08), rough=.74, scale=8, bump=2.6, seed=171)
AMBER_EYE = Material("goblin_amber_eye", "runic_glow", (1.0, .65, .1), (.8, .35, .05), rough=.18, emissive=(1.0, .62, .12), scale=4, seed=172)

# 1. Sinewy hunched torso, neck, and crouched limbs
skin_parts = [
    # Hunched ribcage & abdomen
    ell((0.0, 0.72, 0.04), (0.20, 0.24, 0.16), rings=16, sides=22),
    ell((0.0, 0.54, 0.00), (0.16, 0.15, 0.13), rings=12, sides=18),
    tube((0.0, 0.88, 0.06), (0.0, 1.02, 0.11), 0.085, sides=14, r2=0.075),
]
# Crouched legs & clawed feet (left + right)
for s in (-1, 1):
    skin_parts += [
        tube((s * 0.11, 0.48, 0.00), (s * 0.14, 0.26, 0.07), 0.082, sides=14, r2=0.062),
        ell((s * 0.14, 0.25, 0.07), (0.064, 0.058, 0.064), rings=10, sides=14),
        tube((s * 0.14, 0.25, 0.07), (s * 0.13, 0.06, -0.02), 0.058, sides=14, r2=0.045),
        ell((s * 0.13, 0.04, 0.05), (0.065, 0.038, 0.11), rings=10, sides=14),
        #Sinewy arms & forearms
        ell((s * 0.22, 0.82, 0.04), (0.075, 0.075, 0.075), rings=10, sides=14),
        tube((s * 0.22, 0.80, 0.04), (s * 0.28, 0.58, 0.10), 0.062, sides=14, r2=0.050),
        tube((s * 0.28, 0.58, 0.10), (s * 0.25, 0.42, 0.24), 0.050, sides=14, r2=0.042),
        ell((s * 0.25, 0.40, 0.25), (0.048, 0.045, 0.055), rings=10, sides=12),
    ]

# 2. Head, hooked nose, brow ridge, and long swept goblin ears
head_parts = [
    ell((0.0, 1.08, 0.13), (0.145, 0.135, 0.155), rings=16, sides=22),
    ell((0.0, 1.01, 0.22), (0.095, 0.068, 0.095), rings=12, sides=16),
    cone(0.042, 0.14, (0.0, 1.06, 0.31), sides=12, rot=(78, 0, 0)),
    ell((0.0, 1.13, 0.24), (0.11, 0.032, 0.06), rings=8, sides=14),
]
for s in (-1, 1):
    head_parts.append(
        spline_tube(
            [(s * 0.13, 1.09, 0.11), (s * 0.26, 1.14, 0.04), (s * 0.39, 1.19, -0.05), (s * 0.48, 1.23, -0.12)],
            [0.048, 0.038, 0.022, 0.006], rings=14, sides=10, seed=30 + s
        )
    )

eyes_mesh = merge([
    ell((s * 0.058, 1.09, 0.255), (0.024, 0.018, 0.020), rings=8, sides=12)
    for s in (-1, 1)
])

# 3. Fangs & bone shoulder spikes
bone_parts = [
    cone(0.016, 0.055, (s * 0.042, 0.99, 0.26), sides=8, rot=(-12, 0, -s * 8))
    for s in (-1, 1)
] + [
    cone(0.028, 0.11, (-0.24 + i * 0.04, 0.92, 0.02 + (i - 1) * 0.04), sides=10, rot=(15, 0, 32))
    for i in range(3)
] + [
    cone(0.014, 0.045, (s * (0.09 + c * 0.022), 0.025, 0.15), sides=8, rot=(80, 0, 0))
    for s in (-1, 1) for c in range(3)
]

# 4. Stitched leather jerkin, belt, loincloth, and bracers
leather_parts = [
    cyl_tri(0.21, 0.30, (0.0, 0.70, 0.03), d=1.5, sides=20, r2=0.17, rings=3),
    cyl_tri(0.175, 0.07, (0.0, 0.50, 0.01), d=1.5, sides=20),
    box_tri((0.14, 0.24, 0.025), (0.0, 0.36, 0.13), rot=(-10, 0, 0), d=1.5),
    box_tri((0.14, 0.22, 0.025), (0.0, 0.36, -0.11), rot=(12, 0, 0), d=1.5),
    ell((-0.23, 0.85, 0.03), (0.11, 0.07, 0.11), rings=10, sides=14),
]
for s in (-1, 1):
    leather_parts.append(tube((s * 0.27, 0.54, 0.13), (s * 0.25, 0.43, 0.23), 0.056, sides=12, r2=0.048))

# 5. Left-arm wooden buckler shield with iron boss & rim
buckler_wood = cyl_tri(0.21, 0.032, (0.31, 0.46, 0.24), d=1.2, sides=22, rot=(15, 18, 78))
buckler_iron = merge([
    ell((0.33, 0.46, 0.25), (0.055, 0.055, 0.055), rings=10, sides=14),
    cyl_tri(0.22, 0.020, (0.31, 0.46, 0.24), d=1.2, sides=22, rot=(15, 18, 78)),
])

# 6. Right-hand jagged iron cleaver
cleaver_haft = tube((-0.25, 0.38, 0.12), (-0.25, 0.42, 0.38), 0.022, sides=12)
cleaver_blade = merge([
    box_tri((0.018, 0.14, 0.42), (-0.25, 0.46, 0.58), rot=(8, 0, 0), d=1.5),
    cone(0.018, 0.14, (-0.25, 0.52, 0.81), sides=8, rot=(82, 0, 0)),
    box_tri((0.032, 0.11, 0.035), (-0.25, 0.43, 0.36), d=1.5),
])

root_node = node("mon_forest_goblin_raider", children=[
    node("goblin_hide", merge(skin_parts), GOBLIN_SKIN),
    node("head_skull_ears", merge(head_parts), GOBLIN_SKIN),
    node("head_amber_eyes", eyes_mesh, AMBER_EYE),
    node("head_fangs_claws_spikes", merge(bone_parts), BONEM),
    node("leather_jerkin_gear", merge(leather_parts), LEATHERS),
    node("buckler_wood_plank", buckler_wood, OAKP),
    node("buckler_iron_boss", buckler_iron, DARKSTEEL),
    node("cleaver_wood_grip", cleaver_haft, BEAM),
    node("cleaver_iron_blade", cleaver_blade, DARKSTEEL),
])

if __name__ == "__main__":
    p = export_articulated_character_glb(
        root_node,
        out("monsters", "mon_forest_goblin_raider"),
        tex_size=512,
        is_quadruped=False,
        node_modifiers={
            "leather_jerkin_gear": [("SOLIDIFY", {"thickness": 0.012, "offset": 1.0})],
            "cleaver_iron_blade": [("BEVEL", {"width": 0.005, "segments": 2})],
            "buckler_wood_plank": [("BEVEL", {"width": 0.006, "segments": 1})],
        }
    )
    print("Blender exported:", p)
