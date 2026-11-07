#!/usr/bin/env python3
"""Blender (bpy + bmesh + SOLIDIFY + BEVEL + articulated limb nodes) generator for chr_hero_kaelen_adventurer.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *
root_node = load_asset_root('gen_chr_hero_kaelen_adventurer')

if __name__ == "__main__":
    p = export_articulated_character_glb(
        root_node,
        out("characters", "chr_hero_kaelen_adventurer"),
        tex_size=512,
        is_quadruped=False,
        node_modifiers={
            "midnight_cloak": [("SOLIDIFY", {"thickness": 0.014, "offset": 0.0})],
            "crimson_cloak_lining": [("SOLIDIFY", {"thickness": 0.010, "offset": 0.0})],
            "sword_blade": [("BEVEL", {"width": 0.004, "segments": 1})],
            "sword_grip_guard": [("BEVEL", {"width": 0.005, "segments": 1})],
        }
    )
    print("Blender exported:", p)
