#!/usr/bin/env python3
"""Blender (bpy + bmesh + BEVEL + SOLIDIFY) generator for bld_royal_citadel_keep.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *

if __name__ == "__main__":
    p = export_blender_glb(
        load_asset_root("gen_bld_royal_citadel_keep"),
        out("buildings", "bld_royal_citadel_keep"),
        tex_size=512,
        node_modifiers={
            "arch_voussoirs": [("BEVEL", {"width": 0.022, "segments": 1})],
            "royal_banners": [("SOLIDIFY", {"thickness": 0.02, "offset": 0.0})],
            "gold_trim": [("BEVEL", {"width": 0.015, "segments": 1})],
        }
    )
    print("Blender exported:", p)
