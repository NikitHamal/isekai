#!/usr/bin/env python3
"""Blender (bpy + bmesh + BEVEL + DISPLACE) generator for prp_wooden_wayfinder_signpost.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *

if __name__ == "__main__":
    p = export_blender_glb(
        load_asset_root("gen_prp_wooden_wayfinder_signpost"),
        out("props", "prp_wooden_wayfinder_signpost"),
        tex_size=512,
        node_modifiers={
            "stones": [("DISPLACE", {"tex_type": "VORONOI", "strength": 0.025, "scale": 0.7})],
            "moss": [("SOLIDIFY", {"thickness": 0.015, "offset": 1.0})],
        }
    )
    print("Blender exported:", p)
