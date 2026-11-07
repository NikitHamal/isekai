#!/usr/bin/env python3
"""Generate assets/models/environment/env_sacred_world_tree_canopy.glb: ancient forest tree with gnarled roots, bark trunk & layered canopies."""
from kingdom_lib import *
from vork_forge.dsl import _hash_noise

TREE_BARK = Material("ancient_oak_bark", "wood_grain", (.31, .21, .13), (.14, .09, .05), rough=.90, scale=8, bump=3.8, seed=161)
LEAF_DEEP = Material("forest_canopy_deep", "fbm_noise", (.12, .34, .08), (.05, .18, .03), rough=.88, scale=11, bump=3.2, seed=162)
LEAF_SUN = Material("forest_canopy_sunlit", "fbm_noise", (.22, .48, .11), (.10, .28, .05), rough=.84, scale=10, bump=2.8, seed=163)
ROOT_MOSS = Material("root_hollow_moss", "fbm_noise", (.18, .40, .10), (.08, .22, .04), rough=.95, scale=9, bump=2.5, seed=164)

def foliage_crown(cx, cy, cz, rx, ry, rz, rings=18, sides=24, seed=1):
    """Billowing multi-lobed 3D leaf canopy cluster with organic noise displacement."""
    r = np.random.RandomState(seed)
    th = np.linspace(np.pi, 0, rings + 1)[:, None]
    ph = np.linspace(0, 2 * np.pi, sides + 1)[None, :]
    lobe = (1.0
            + 0.16 * np.cos(5 * ph + r.rand() * 6.28) * np.sin(th)
            + 0.12 * np.sin(3 * th + 4 * ph + r.rand() * 6.28)
            + 0.08 * np.cos(7 * ph - 2 * th))
    X = np.sin(th) * np.cos(ph) * rx * lobe
    Y = np.cos(th) * ry * (0.88 + 0.15 * np.sin(th * 2)) + 0.0 * ph
    Z = np.sin(th) * np.sin(ph) * rz * lobe
    P = np.stack([X, Y, Z], -1)
    n1 = _hash_noise(P * 0.9, seed=seed + 10, freq=1.4)
    n2 = _hash_noise(P * 2.1, seed=seed + 20, freq=1.8)
    disp = 1.0 + 0.18 * n1 + 0.09 * n2
    P[..., 0] = cx + P[..., 0] * disp
    P[..., 1] = cy + P[..., 1] * (1.0 + 0.12 * n1)
    P[..., 2] = cz + P[..., 2] * disp
    return grid(P, uscale=3.0, vscale=2.5, closed_u=True, cap=False)

# 1. Fluted main trunk + sweeping primary and secondary limbs
trunk_parts = [
    spline_tube(
        [(0, -0.1, 0), (0.08, 1.4, -0.05), (-0.06, 3.0, 0.06), (0.04, 4.6, 0.0), (0.0, 5.8, -0.04)],
        [0.95, 0.72, 0.58, 0.46, 0.34],
        rings=32, sides=24, bark_disp=0.05, seed=11
    )
]

branch_specs = [
    ([(0.0, 4.1, 0.0), (1.1, 4.9, 0.6), (2.3, 5.7, 1.2), (3.2, 6.2, 1.6)], [0.36, 0.28, 0.20, 0.12], 21),
    ([(0.0, 4.3, 0.0), (-1.2, 5.1, 0.7), (-2.4, 5.8, 1.3), (-3.3, 6.3, 1.7)], [0.35, 0.27, 0.19, 0.11], 22),
    ([(0.0, 4.4, 0.0), (0.8, 5.2, -1.1), (1.8, 6.0, -2.2), (2.5, 6.5, -2.9)], [0.34, 0.26, 0.18, 0.11], 23),
    ([(0.0, 4.2, 0.0), (-0.9, 5.0, -1.0), (-2.0, 5.8, -2.1), (-2.7, 6.4, -2.8)], [0.34, 0.25, 0.18, 0.10], 24),
    ([(0.0, 4.8, 0.0), (1.3, 5.8, -0.2), (2.6, 6.7, -0.4)], [0.30, 0.22, 0.12], 25),
    ([(0.0, 4.9, 0.0), (-1.3, 5.9, -0.1), (-2.5, 6.8, -0.3)], [0.30, 0.22, 0.12], 26),
    ([(0.0, 5.2, 0.0), (0.2, 6.4, 1.2), (0.4, 7.3, 2.2)], [0.28, 0.20, 0.11], 27),
    ([(0.0, 5.3, 0.0), (-0.2, 6.5, -1.1), (-0.3, 7.4, -2.0)], [0.28, 0.20, 0.11], 28),
]
for pts, rads, sd in branch_specs:
    trunk_parts.append(spline_tube(pts, rads, rings=20, sides=14, bark_disp=0.035, seed=sd))

# 2. Gnarled spreading buttress roots
roots = []
moss_roots = []
for i in range(9):
    ang = i * 2 * np.pi / 9 + 0.15 * np.sin(i * 2.1)
    ca, sa = np.cos(ang), np.sin(ang)
    pts = [
        (ca * 0.45, 1.35, sa * 0.45),
        (ca * 0.95, 0.65, sa * 0.95),
        (ca * 1.65 + sa * 0.18, 0.22, sa * 1.65 - ca * 0.18),
        (ca * 2.35 + sa * 0.28, -0.06, sa * 2.35 - ca * 0.28),
    ]
    roots.append(spline_tube(pts, [0.34, 0.26, 0.17, 0.07], rings=20, sides=12, bark_disp=0.03, seed=40 + i))
    moss_roots.append(foliage_crown(ca * 1.15, 0.28, sa * 1.15, 0.42, 0.22, 0.42, rings=8, sides=12, seed=140 + i))

# 3. Layered deep-emerald lower leaf canopy boughs
lower_canopy = [
    foliage_crown(2.8, 6.2, 1.4, 2.2, 1.35, 2.1, rings=18, sides=24, seed=61),
    foliage_crown(-2.9, 6.3, 1.5, 2.2, 1.35, 2.1, rings=18, sides=24, seed=62),
    foliage_crown(2.2, 6.4, -2.5, 2.1, 1.3, 2.0, rings=18, sides=24, seed=63),
    foliage_crown(-2.3, 6.3, -2.4, 2.1, 1.3, 2.0, rings=18, sides=24, seed=64),
    foliage_crown(2.6, 6.7, -0.3, 2.0, 1.25, 1.9, rings=16, sides=22, seed=65),
    foliage_crown(-2.5, 6.8, -0.2, 2.0, 1.25, 1.9, rings=16, sides=22, seed=66),
    foliage_crown(0.3, 7.0, 2.2, 2.1, 1.3, 2.0, rings=16, sides=22, seed=67),
    foliage_crown(-0.3, 7.1, -2.1, 2.1, 1.3, 2.0, rings=16, sides=22, seed=68),
]

# 4. Sunlit upper crown domes
upper_canopy = [
    foliage_crown(0.0, 8.2, 0.0, 3.1, 1.85, 3.0, rings=20, sides=28, seed=81),
    foliage_crown(1.5, 7.7, 0.8, 2.2, 1.45, 2.1, rings=16, sides=22, seed=82),
    foliage_crown(-1.5, 7.8, 0.7, 2.2, 1.45, 2.1, rings=16, sides=22, seed=83),
    foliage_crown(1.2, 7.6, -1.2, 2.1, 1.4, 2.0, rings=16, sides=22, seed=84),
    foliage_crown(-1.3, 7.7, -1.1, 2.1, 1.4, 2.0, rings=16, sides=22, seed=85),
    foliage_crown(0.0, 9.3, 0.1, 2.0, 1.3, 1.9, rings=16, sides=22, seed=86),
]

root_node = node("env_sacred_world_tree_canopy", children=[
    node("ancient_bark_trunk", merge(trunk_parts), TREE_BARK),
    node("gnarled_buttress_roots", merge(roots), TREE_BARK),
    node("root_hollow_moss", merge(moss_roots), ROOT_MOSS),
    node("lower_leaf_canopy", merge(lower_canopy), LEAF_DEEP),
    node("upper_sunlit_canopy", merge(upper_canopy), LEAF_SUN),
])

if __name__ == "__main__":
    p = compile_glb(root_node, out("environment", "env_sacred_world_tree_canopy"), tex_size=1024)
    print("Wrote", p)
