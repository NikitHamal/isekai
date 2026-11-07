#!/usr/bin/env python3
"""Blender (bpy + bmesh + DISPLACE Clouds fur + articulated quadruped nodes) generator for mon_shadow_direwolf_alpha.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *
root_node = load_asset_root('gen_mon_shadow_direwolf_alpha')

if __name__ == "__main__":
    p = export_articulated_character_glb(
        root_node,
        out("monsters", "mon_shadow_direwolf_alpha"),
        tex_size=512,
        is_quadruped=True,
        node_modifiers={
            "shadow_fur_body": [("DISPLACE", {"tex_type": "CLOUDS", "strength": 0.015, "scale": 0.5})],
        }
    )
    print("Blender exported:", p)
