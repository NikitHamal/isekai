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
EMERALD = Material("emerald_tunic", "woven_cloth", (.08, .42, .2), (.04, .24, .1), rough=.85, scale=8, bump=2.5, seed=31)
LEATHER = Material("brown_leather", "woven_cloth", (.32, .18, .09), (.16, .09, .05), rough=.65, scale=10, bump=3, seed=32)
BEIGE = Material("beige_cloth", "woven_cloth", (.78, .68, .5), (.55, .46, .32), rough=.9, scale=9, bump=2, seed=33)
SKIN = Material("skin", "fbm_noise", (.93, .72, .58), (.82, .6, .47), rough=.6, scale=4, bump=.4, seed=34)
HAIR = Material("hair", "wood_grain", (.36, .2, .1), (.2, .1, .05), rough=.55, scale=9, bump=1.5, seed=35)
EYEG = Material("eye_glow", "runic_glow", (.1, .6, .3), (.05, .4, .2), rough=.2, emissive=(.2, 1, .5), scale=3, seed=36)
def folded(profile, folds=9, amp=.07, seg=72, zs=.75):
    """Lathe with radial cloth folds; profile [(r, y)], elliptical depth zs."""
    p = np.asarray(profile, float); ph = np.linspace(0, 2*np.pi, seg + 1)[None]; r = p[:, :1] * (1 + amp * np.sin(folds * ph) * np.clip((1.0 - p[:, 1:] * .0), 0, 1) * np.linspace(1, .2, len(p))[::-1][:, None])
    return grid(np.stack([r * np.cos(ph), p[:, 1:] + 0 * ph, r * np.sin(ph) * zs], -1), uscale=3.0)
LUMEN = Material("lumen_core", "runic_glow", (.7, 1, 1), (.3, .8, 1), rough=.15, emissive=(.6, 1, 1), scale=4, seed=41)
WINGM = Material("sylph_wing", "fbm_noise", (.6, .95, 1), (.85, .8, 1), rough=.2, emissive=(.25, .6, .8), scale=6, bump=.3, alpha=.6, seed=42)
VEIN = Material("wing_vein", "runic_glow", (.9, 1, 1), (.6, .9, 1), rough=.2, emissive=(.9, 1, 1), scale=6, seed=43)
HALO = Material("mana_halo", "runic_glow", (1, .85, .4), (.9, .6, .2), rough=.2, emissive=(1, .8, .3), scale=5, seed=44)
STEEL = Material("polished_steel", "hammered_metal", (.7, .73, .78), (.45, .48, .55), rough=.3, metal=1.0, scale=4, bump=.6, seed=45)
OAK = Material("oak_planks", "wood_grain", (.5, .33, .18), (.28, .17, .09), rough=.75, scale=6, bump=2, seed=46)
def wing(root, ang, L, W, bend=.15, n=36, m=22, flip=False):
    """Sylph wing blade in XY plane rotated by ang (deg) about Z from root; returns surface mesh."""
    a = np.radians(ang); d = np.array([np.cos(a), np.sin(a), 0]); p = np.array([-np.sin(a), np.cos(a), 0]); P = np.zeros((n, m, 3))
    for i in range(n):
        s = i / (n - 1); w = W * np.sin(np.pi * s ** .75) ** .9 * (1 + .25 * np.sin(3 * np.pi * s)) + .004
        for j in range(m):
            t = j / (m - 1) * 2 - 1; P[i, j] = root + d * L * s + p * t * w * (1.0 + .3 * s * (t > 0)) + np.array([0, 0, 1]) * (-bend * s * s * L + .02 * np.cos(t * 2) * w)
    return grid(P, closed_u=False, flip=flip)
