#!/usr/bin/env python3
"""Blender (bpy + bmesh + BEVEL + SUBSURF) generator for prp_ornate_treasure_chest.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *

if __name__ == "__main__":
    p = export_blender_glb(
        load_asset_root("gen_prp_ornate_treasure_chest"),
        out("props", "prp_ornate_treasure_chest"),
        tex_size=512,
        node_modifiers={
            "body": [("BEVEL", {"width": 0.012, "segments": 2})],
            "straps": [("BEVEL", {"width": 0.006, "segments": 1})],
        }
    )
    print("Blender exported:", p)
