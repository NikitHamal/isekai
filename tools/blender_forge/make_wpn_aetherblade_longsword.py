#!/usr/bin/env python3
"""Blender (bpy + bmesh + BEVEL + SUBSURF) generator for wpn_aetherblade_longsword.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *

if __name__ == "__main__":
    p = export_blender_glb(
        load_asset_root("gen_wpn_aetherblade_longsword"),
        out("weapons", "wpn_aetherblade_longsword"),
        tex_size=512,
        node_modifiers={
            "crossguard": [("BEVEL", {"width": 0.004, "segments": 2})],
            "pommel": [("SUBSURF", {"levels": 1})],
        }
    )
    print("Blender exported:", p)
