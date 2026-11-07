#!/usr/bin/env python3
"""Blender (bpy + bmesh + SOLIDIFY + BEVEL + DISPLACE + articulated limb nodes) generator for mon_orc_warlord_berserker.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *
root_node = load_asset_root('gen_mon_orc_warlord_berserker')

if __name__ == "__main__":
    p = export_articulated_character_glb(
        root_node,
        out("monsters", "mon_orc_warlord_berserker"),
        tex_size=512,
        is_quadruped=False,
        node_modifiers={
            "iron_pauldrons_spikes": [("BEVEL", {"width": 0.008, "segments": 1})],
            "greataxe_blades": [("BEVEL", {"width": 0.007, "segments": 1})],
        }
    )
    print("Blender exported:", p)
