#!/usr/bin/env python3
"""Blender (bpy + bmesh + BEVEL + SOLIDIFY) generator for wpn_royal_crest_heater_shield.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *

if __name__ == "__main__":
    p = export_blender_glb(
        load_asset_root("gen_wpn_royal_crest_heater_shield"),
        out("weapons", "wpn_royal_crest_heater_shield"),
        tex_size=512,
        node_modifiers={
            "steel_bands": [("BEVEL", {"width": 0.003, "segments": 1})],
            "crest_crown": [("BEVEL", {"width": 0.003, "segments": 1})],
        }
    )
    print("Blender exported:", p)
