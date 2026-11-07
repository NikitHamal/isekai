#!/usr/bin/env python3
"""Blender (bpy + bmesh + BEVEL + SOLIDIFY) generator for bld_medieval_tavern_inn.glb."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *

# 1. Cut-stone foundation & ground-floor walls (main hall + projecting front gable wing)
plinth = merge([
    box_tri((11.4, 0.50, 8.2), (0.0, 0.25, 0.0), d=0.4),
    box_tri((4.6, 0.50, 3.2), (2.8, 0.25, 5.2), d=0.4),
])

ground_walls = merge([
    block_wall(-5.4, 5.4, 0.50, 3.6, -3.8, 0.44, seed=21),
    block_wall(-5.4, 0.5, 0.50, 3.6, 3.8, 0.44, seed=22, holes=[(-2.8, -1.0, 0.50, 2.7)]),
    block_wall(-3.8, 3.8, 0.50, 3.6, -5.4, 0.44, seed=23, axis=1),
    block_wall(-3.8, 6.4, 0.50, 3.6, 5.0, 0.44, seed=24, axis=1),
    block_wall(0.6, 5.0, 0.50, 3.6, 6.4, 0.44, seed=25),
    arch_opening(-1.9, 0.50, 1.8, 1.7, 3.85, 0.52, n=13),
])

# 2. Jetted second-story lime-plaster walls & gable triangles
upper_plaster = merge([
    box_tri((11.2, 3.1, 8.0), (0.0, 5.15, 0.0), d=0.35),
    box_tri((4.6, 3.1, 3.2), (2.8, 5.15, 5.1), d=0.35),
    poly_prism([(-3.9, 6.7), (3.9, 6.7), (0.0, 9.5)], 0.38, (-5.45, 0.0, 0.0), rot=(0, 90, 0)),
    poly_prism([(-3.9, 6.7), (3.9, 6.7), (0.0, 9.5)], 0.38, (5.45, 0.0, 0.0), rot=(0, 90, 0)),
    poly_prism([(0.5, 6.7), (5.1, 6.7), (2.8, 9.3)], 0.38, (0.0, 0.0, 6.55)),
])

# 3. Half-timbered oak beam framing, porch balcony & roof trusses
timbers = []
for x in np.linspace(-5.5, 5.5, 7):
    for z in (-4.02, 4.02):
        timbers.append(box_tri((0.22, 3.2, 0.22), (x, 5.15, z), d=0.6))
for z in (-4.02, 4.02):
    timbers += [
        box_tri((11.3, 0.24, 0.26), (0.0, 3.65, z), d=0.6),
        box_tri((11.3, 0.24, 0.26), (0.0, 6.68, z), d=0.6),
    ]
# Second-floor wooden balcony over front entrance (x in [-5.2, 0.4], z in [3.9, 5.3])
balcony_wood = merge([
    box_tri((5.6, 0.18, 1.5), (-2.4, 3.60, 4.65), d=0.6),
    box_tri((5.6, 0.14, 0.14), (-2.4, 4.45, 5.32), d=0.6),
] + [
    box_tri((0.12, 0.85, 0.12), (x, 4.02, 5.32), d=0.6)
    for x in np.linspace(-5.0, 0.2, 11)
] + [
    box_tri((0.22, 3.1, 0.22), (x, 2.05, 5.25), d=0.6)
    for x in (-5.0, -2.4, 0.2)
])

# 4. Intersecting steep slate gable roofs + twin tall stone chimneys
slate_main, ridge_main = gable_roof(11.6, 4.1, 2.85, (0.0, 6.65, 0.0), over=0.45, lip_rows=12)
slate_wing, ridge_wing = gable_roof(3.4, 2.45, 2.65, (0.0, 0.0, 0.0), over=0.40, lip_rows=8)
slate_wing = slate_wing.tf((2.8, 6.65, 5.1), (0, 90, 0))
ridge_wing = ridge_wing.tf((2.8, 6.65, 5.1), (0, 90, 0))

chimneys = merge([
    box_tri((1.1, 3.6, 1.1), (-3.8, 8.8, -2.2), d=0.45),
    box_tri((1.3, 0.28, 1.3), (-3.8, 10.65, -2.2), d=0.45),
    box_tri((1.1, 3.4, 1.1), (4.2, 8.7, -2.0), d=0.45),
    box_tri((1.3, 0.28, 1.3), (4.2, 10.45, -2.0), d=0.45),
])

# 5. Outdoor ale barrels, oak door, warm glowing tavern windows & golden inn sign
barrels_and_door = merge([
    box_tri((1.6, 2.15, 0.16), (-1.9, 1.55, 3.82), d=0.8),
] + [
    cyl_tri(0.38, 0.82, (-4.2 + i * 0.85, 0.90, 4.6), d=0.9, sides=16, r2=0.34)
    for i in range(3)
])

lit_windows = merge([
    box_tri((1.1, 1.2, 0.12), (-3.8, 5.2, 4.02), d=0.5),
    box_tri((1.1, 1.2, 0.12), (-1.2, 5.2, 4.02), d=0.5),
    box_tri((1.3, 1.25, 0.12), (2.8, 5.2, 6.72), d=0.5),
    box_tri((1.3, 1.25, 0.12), (2.8, 2.0, 6.45), d=0.5),
    box_tri((1.2, 1.2, 0.12), (-2.5, 5.2, -4.02), d=0.5),
    box_tri((1.2, 1.2, 0.12), (2.2, 5.2, -4.02), d=0.5),
])

inn_sign = merge([
    beam((0.4, 4.8, 5.2), (1.5, 4.8, 5.2), 0.10),
    cyl_tri(0.45, 0.08, (1.15, 4.25, 5.2), d=0.9, sides=20, rot=(90, 0, 0)),
])

root_node = node("bld_medieval_tavern_inn", children=[
    node("stone_plinth", plinth, DARKSTONE),
    node("ground_masonry_walls", ground_walls, CASTLE),
    node("upper_plaster_walls", upper_plaster, PLASTER),
    node("half_timber_beams", merge(timbers), BEAM),
    node("balcony_and_porch", balcony_wood, OAKP),
    node("slate_roof_shingles", merge([slate_main, slate_wing]), SLATE),
    node("roof_ridges_chimneys", merge([ridge_main, ridge_wing, chimneys]), STONEF),
    node("ale_barrels_and_door", barrels_and_door, OAKP),
    node("warm_tavern_windows", lit_windows, GLASSLIT),
    node("golden_inn_sign", inn_sign, GOLDM),
])

if __name__ == "__main__":
    p = export_blender_glb(
        root_node,
        out("buildings", "bld_medieval_tavern_inn"),
        tex_size=512,
        node_modifiers={
            "stone_plinth": [("BEVEL", {"width": 0.025, "segments": 1})],
            "roof_ridges_chimneys": [("BEVEL", {"width": 0.02, "segments": 1})],
            "golden_inn_sign": [("BEVEL", {"width": 0.01, "segments": 1})],
            "half_timber_beams": [("BEVEL", {"width": 0.015, "segments": 1})],
            "balcony_and_porch": [("BEVEL", {"width": 0.015, "segments": 1})],
        }
    )
    print("Blender exported:", p)
