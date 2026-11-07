#!/usr/bin/env python3
"""Blender (bpy + bmesh + SOLIDIFY + BEVEL + articulated limb nodes) generator for chr_ally_garrick_royal_paladin.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *
root_node = load_asset_root('gen_chr_ally_garrick_royal_paladin')

if __name__ == "__main__":
    p = export_articulated_character_glb(
        root_node,
        out("characters", "chr_ally_garrick_royal_paladin"),
        tex_size=512,
        is_quadruped=False,
        node_modifiers={
            "royal_cape": [("SOLIDIFY", {"thickness": 0.016, "offset": 0.0})],
            "broadsword_blade": [("BEVEL", {"width": 0.005, "segments": 1})],
            "lion_gold_crests": [("BEVEL", {"width": 0.006, "segments": 1})],
        }
    )
    print("Blender exported:", p)
