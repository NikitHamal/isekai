#!/usr/bin/env python3
"""Generate assets/models/environment/env_mossy_forest_cliff_modular.glb: 360-degree sculpted mountain crag & mossy terraced outcrops."""
from kingdom_lib import *
from vork_forge.dsl import _hash_noise

CRAG_ROCK = Material("crag_limestone", "fbm_noise", (.52, .50, .45), (.28, .27, .24), rough=.94, scale=7, bump=4.0, seed=151)
CRAG_SLATE = Material("crag_basal_slate", "fbm_noise", (.36, .35, .33), (.18, .18, .17), rough=.96, scale=9, bump=4.5, seed=152)
CRAG_MOSS = Material("crag_alpine_moss", "fbm_noise", (.22, .42, .11), (.10, .23, .05), rough=.98, scale=10, bump=3.0, seed=153)

def sculpted_spire(cx, cy, cz, rx, rz, h, rings=30, sides=32, seed=1, taper=0.38, tilt_x=0.0, tilt_z=0.0):
    """Closed 3D jagged rock crag with stratified ledges, ridged multi-octave noise, and chiseled crest."""
    r = np.random.RandomState(seed)
    u = np.linspace(0, 1, rings)[:, None]
    th = np.linspace(0, 2 * np.pi, sides + 1)[None, :]
    terrace = 0.08 * np.sin(u * np.pi * 6.0) + 0.035 * np.cos(u * np.pi * 11.0)
    crown = np.clip((1.0 - u) / 0.16, 0.0, 1.0) ** 0.55
    prof = ((1.0 - (1.0 - taper) * (u ** 0.8)) + terrace * (1.0 - u * 0.6)) * crown
    prof = np.maximum(0.02, prof)
    ang_mod = (1.0
               + 0.20 * np.cos(3 * th + r.rand() * 6.28)
               + 0.13 * np.sin(5 * th + u * 2.2 + r.rand() * 6.28)
               + 0.08 * np.cos(7 * th - u * 3.5 + r.rand() * 6.28))
    X0 = np.cos(th) * rx * prof * ang_mod + u * h * tilt_x
    Z0 = np.sin(th) * rz * prof * ang_mod + u * h * tilt_z
    Y0 = (u - 0.03) * h + 0.0 * th
    P = np.stack([X0, Y0, Z0], -1)
    n1 = _hash_noise(P * 0.45, seed=seed + 10, freq=1.2)
    n2 = _hash_noise(P * 1.15, seed=seed + 20, freq=1.6)
    n3 = np.abs(_hash_noise(P * 2.3, seed=seed + 30, freq=2.0))
    radial_disp = (0.34 * n1 + 0.16 * n2 - 0.12 * n3) * crown
    P[..., 0] += np.cos(th) * rx * radial_disp
    P[..., 2] += np.sin(th) * rz * radial_disp
    P[..., 1] += 0.22 * n2 * (1.0 - 0.5 * u)
    P[-1, :, 0] = P[-2, :, 0].mean()
    P[-1, :, 2] = P[-2, :, 2].mean()
    P[-1, :, 1] = P[-2, :, 1].max() + 0.08
    P[..., 0] += cx; P[..., 1] += cy; P[..., 2] += cz
    return grid(P, uscale=3.5, vscale=3.0, closed_u=True, cap=True)

def extract_moss_mantle(rock_mesh, ny_min=0.44, y_min=0.8, thickness=0.07):
    """Extract upward-facing rock terrace triangles and thicken them into a conforming mossy turf layer."""
    V = rock_mesh.V; F = rock_mesh.F; N = rock_mesh.normals()
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    fl = np.linalg.norm(fn, axis=1, keepdims=True) + 1e-12
    fn = fn / fl
    fc = V[F].mean(1)
    keep = (fn[:, 1] > ny_min) & (fc[:, 1] > y_min)
    Fk = F[keep]
    used = np.unique(Fk)
    remap = np.zeros(len(V), dtype=np.int64)
    remap[used] = np.arange(len(used))
    Vm = V[used] + N[used] * thickness + np.array([0.0, 0.03, 0.0])
    UVm = rock_mesh.UV[used] * 1.5
    return Mesh(Vm, remap[Fk], UVm)

main_crags = merge([
    sculpted_spire(0.0, 0.0, 0.0, 3.9, 2.9, 7.6, rings=30, sides=32, seed=11, taper=0.42, tilt_x=0.05, tilt_z=0.04),
    sculpted_spire(-3.3, 0.0, 0.3, 2.8, 2.4, 5.8, rings=26, sides=28, seed=23, taper=0.45, tilt_x=-0.06, tilt_z=0.03),
    sculpted_spire(3.4, 0.0, -0.2, 2.9, 2.5, 6.2, rings=26, sides=28, seed=37, taper=0.44, tilt_x=0.07, tilt_z=-0.03),
])

basal_rocks = merge([
    sculpted_spire(-1.8, 0.0, 2.0, 2.1, 1.7, 3.2, rings=18, sides=22, seed=41, taper=0.52, tilt_x=-0.04, tilt_z=0.08),
    sculpted_spire(2.0, 0.0, 1.8, 2.2, 1.6, 3.5, rings=18, sides=22, seed=53, taper=0.50, tilt_x=0.05, tilt_z=0.07),
    sculpted_spire(0.2, 0.0, -1.9, 2.6, 1.9, 4.1, rings=18, sides=22, seed=67, taper=0.48, tilt_x=0.0, tilt_z=-0.07),
    sculpted_spire(-4.7, 0.0, 1.2, 1.6, 1.4, 2.3, rings=14, sides=18, seed=79, taper=0.55),
    sculpted_spire(4.8, 0.0, 1.0, 1.7, 1.3, 2.5, rings=14, sides=18, seed=83, taper=0.54),
])

moss_mesh = merge([
    extract_moss_mantle(main_crags, ny_min=0.38, y_min=1.1, thickness=0.065),
    extract_moss_mantle(basal_rocks, ny_min=0.42, y_min=0.6, thickness=0.055),
])

# Gnarled roots hugging the lower rock crevices
r = np.random.RandomState(108)
roots = []
for i in range(7):
    ang = -2.2 + i * 0.72
    ca, sa = np.cos(ang), np.sin(ang)
    pts = [
        (ca * 2.1, 3.6 + (i % 2) * 0.5, sa * 1.7),
        (ca * 2.6 + r.randn() * 0.12, 2.4, sa * 2.1 + r.randn() * 0.12),
        (ca * 3.1 + r.randn() * 0.15, 1.2, sa * 2.5 + r.randn() * 0.15),
        (ca * 3.6 + r.randn() * 0.12, 0.1, sa * 2.9 + r.randn() * 0.12),
    ]
    roots.append(spline_tube(pts, [0.14, 0.11, 0.08, 0.04], rings=16, sides=8, bark_disp=0.02, seed=200 + i))

root_node = node("env_mossy_forest_cliff_modular", children=[
    node("crag_main_buttress", main_crags, CRAG_ROCK),
    node("dark_basal_slate", basal_rocks, CRAG_SLATE),
    node("moss_terraces", moss_mesh, CRAG_MOSS),
    node("gnarled_crevice_roots", merge(roots), BARK),
])

if __name__ == "__main__":
    p = compile_glb(root_node, out("environment", "env_mossy_forest_cliff_modular"), tex_size=1024)
    print("Wrote", p)
