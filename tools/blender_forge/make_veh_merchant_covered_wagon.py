#!/usr/bin/env python3
"""Blender (bpy + bmesh + BEVEL + SOLIDIFY + DISPLACE) generator for veh_merchant_covered_wagon.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *

if __name__ == "__main__":
    p = export_blender_glb(
        load_asset_root("gen_veh_merchant_covered_wagon"),
        out("vehicles", "veh_merchant_covered_wagon"),
        tex_size=512,
        node_modifiers={
            "canvas_canopy": [("SOLIDIFY", {"thickness": 0.018, "offset": 0.0})],
            "cargo_sacks": [("DISPLACE", {"tex_type": "CLOUDS", "strength": 0.02, "scale": 0.5})],
            "lit_lantern": [("BEVEL", {"width": 0.006, "segments": 1})],
        }
    )
    print("Blender exported:", p)
