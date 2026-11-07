#!/usr/bin/env python3
"""Blender (bpy + bmesh + BEVEL + SOLIDIFY) generator for bld_valoria_adventurer_guild.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *

if __name__ == "__main__":
    p = export_blender_glb(
        load_asset_root("gen_bld_valoria_adventurer_guild"),
        out("buildings", "bld_valoria_adventurer_guild"),
        tex_size=512,
        node_modifiers={
            "plinth_stone": [("BEVEL", {"width": 0.03, "segments": 2})],
            "arch_voussoirs": [("BEVEL", {"width": 0.018, "segments": 1})],
            "ridge_caps": [("BEVEL", {"width": 0.02, "segments": 1})],
            "sign_emblem": [("BEVEL", {"width": 0.01, "segments": 1})],
        }
    )
    print("Blender exported:", p)
