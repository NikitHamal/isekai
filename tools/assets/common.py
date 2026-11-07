import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from vork_forge import *
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
def out(cat, slug): return os.path.join(ROOT, "assets", "models", cat, slug + ".glb")
BARK = Material("bark", "wood_grain", (.30, .20, .12), (.13, .08, .05), rough=.9, scale=5, bump=3, seed=2)
TIMBER = Material("timber", "wood_grain", (.45, .30, .17), (.25, .15, .08), rough=.8, scale=7, bump=2, seed=4)
STONE = Material("stone", "voronoi_stone", (.55, .55, .5), (.32, .33, .3), rough=.92, scale=5, bump=3, seed=6)
MOSS = Material("moss", "fbm_noise", (.28, .5, .12), (.12, .28, .06), rough=1.0, scale=8, bump=3, seed=8)
ROPE = Material("rope", "woven_cloth", (.72, .6, .38), (.45, .36, .2), rough=.95, scale=6, bump=3, seed=9)
IRON = Material("iron", "hammered_metal", (.42, .42, .45), (.2, .2, .22), rough=.5, metal=.9, scale=5, seed=10)
AMBER = Material("amber_glow", "runic_glow", (1, .62, .15), (.9, .35, .05), rough=.2, emissive=(1, .6, .15), scale=5, alpha=1.0, seed=11)
RUBY = Material("ruby_glow", "runic_glow", (.8, .05, .08), (.5, .0, .05), rough=.15, emissive=(1, .1, .15), scale=4, seed=12)
GOLD = Material("gold", "hammered_metal", (.95, .75, .3), (.7, .5, .15), rough=.3, metal=1.0, scale=6, seed=13)
