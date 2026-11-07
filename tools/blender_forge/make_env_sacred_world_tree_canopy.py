#!/usr/bin/env python3
"""Blender (bpy + bmesh + DISPLACE Wood/Clouds/Voronoi + SUBSURF) generator for env_sacred_world_tree_canopy.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *
from assets.gen_env_sacred_world_tree_canopy import root_node

if __name__ == "__main__":
    p = export_blender_glb(
        root_node,
        out("environment", "env_sacred_world_tree_canopy"),
        tex_size=512,
        node_modifiers={
            "ancient_bark_trunk": [("DISPLACE", {"tex_type": "WOOD", "strength": 0.025, "scale": 0.6})],
            "gnarled_buttress_roots": [("DISPLACE", {"tex_type": "WOOD", "strength": 0.02, "scale": 0.6})],
            "root_hollow_moss": [("SOLIDIFY", {"thickness": 0.03, "offset": 1.0})],
            "lower_leaf_canopy": [("DISPLACE", {"tex_type": "CLOUDS", "strength": 0.11, "scale": 0.85})],
            "upper_sunlit_canopy": [("DISPLACE", {"tex_type": "VORONOI", "strength": 0.09, "scale": 0.9})],
        }
    )
    print("Blender exported:", p)
