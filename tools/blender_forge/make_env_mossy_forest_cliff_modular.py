#!/usr/bin/env python3
"""Blender (bpy + bmesh + DISPLACE Voronoi/Clouds + SOLIDIFY + SUBSURF) generator for env_mossy_forest_cliff_modular.glb."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blender_forge.blender_utils import *
from assets.gen_env_mossy_forest_cliff_modular import root_node

if __name__ == "__main__":
    p = export_blender_glb(
        root_node,
        out("environment", "env_mossy_forest_cliff_modular"),
        tex_size=512,
        node_modifiers={
            "crag_main_buttress": [("DISPLACE", {"tex_type": "VORONOI", "strength": 0.12, "scale": 0.85})],
            "dark_basal_slate": [("DISPLACE", {"tex_type": "CLOUDS", "strength": 0.10, "scale": 0.75})],
            "moss_terraces": [("SOLIDIFY", {"thickness": 0.04, "offset": 1.0})],
            "gnarled_crevice_roots": [("SUBSURF", {"levels": 1})],
        }
    )
    print("Blender exported:", p)
