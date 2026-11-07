from common import *
import numpy as np
from vork_forge.dsl import _hash_noise
W, H, n, m = 14.0, 8.0, 60, 84
xs = np.linspace(-W/2, W/2, m); ys = np.linspace(0, H, n); X, Y = np.meshgrid(xs, ys)
def disp(X, Y):
    pts = np.stack([X.ravel(), Y.ravel(), np.zeros(X.size)], 1); a = _hash_noise(pts, 3, .55).reshape(X.shape); b = _hash_noise(pts, 9, 2.2).reshape(X.shape)
    strata = np.sin(Y * 2.1 + a * 3.0); ledge = np.tanh(strata * 3.0) * .22 + (Y * .06)
    return a * 1.1 + b * .18 + ledge + .45 * np.sin(X * .45 + a)
Z = disp(X, Y); Z *= np.clip(Y / .8, 0, 1) ** .5 * .9 + .1; Z[0] = Z[0] * 0 - .05
P = np.stack([X, Y, Z], -1); front = grid(P, closed_u=False, flip=True)
back = grid(np.stack([X[::59], Y[::59], 0 * X[::59] - 2.2], -1), closed_u=False)
top = grid(np.stack([X[-1:].repeat(2, 0), Y[-1:].repeat(2, 0), np.array([Z[-1], 0 * Z[-1] - 2.2])], -1), closed_u=False)
cen = front.V[front.F].mean(1); nrm = np.cross(front.V[front.F[:, 1]] - front.V[front.F[:, 0]], front.V[front.F[:, 2]] - front.V[front.F[:, 0]]); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
mossmask = ((nrm[:, 1] > .38) | (_hash_noise(cen, 5, .9) > .12 + (.25 - cen[:, 1] / H * .5))) & (cen[:, 1] > .5)
moss = Mesh(front.V + np.array([0, .012, .03]), front.F[mossmask], front.UV)
R = np.random.RandomState(4); rocks = merge([sphere(.5 + R.rand() * .7, (R.uniform(-6.2, 6.2), R.uniform(.7, 6.5), 0), (1.5, .55, 1), 10, 14).tf(rot=(R.uniform(-10, 10), R.uniform(-30, 30), R.uniform(-8, 8))) for _ in range(16)])
roots = [spline_tube([(x, 7.9, .1), (x + R.uniform(-.8, .8), 7.2, .9), (x + R.uniform(-1, 1), 6.0, 1.3), (x + R.uniform(-1.2, 1.2), 4.6 - R.rand() * 1.3, .6)], [.2, .14, .09, .03], rings=30, sides=12, bark_disp=.2, seed=i) for i, x in enumerate(np.linspace(-6, 6, 7))]
roots += [spline_tube([(x, 7.9, .1), (x + R.uniform(-.5, .5), 6.8, .55), (x + R.uniform(-.8, .8), 5.6, .9)], [.1, .07, .02], rings=20, sides=8, bark_disp=.15, seed=30 + i) for i, x in enumerate(np.linspace(-5.2, 5.2, 6))]
slabs = [box((1.5 + R.rand() * .7, .22, 1.1 + R.rand() * .5), (-5.4 + (i % 6) * 2.15 + R.randn() * .1, .11 + (i // 6) * .22, 1.9 + (i // 6) * 1.2 + R.randn() * .1), (0, R.randn() * 4, 0), seg=4) for i in range(18)]
root_node = node("env_mossy_forest_cliff_modular", None, None, [node("limestone_wall", merge([front, back, top]), LIME), node("moss_blanket", moss, MOSS), node("ledge_boulders", Mesh(rocks.V + np.array([0, 0, -1.1]), rocks.F, rocks.UV), LIME),
    node("overhanging_roots", merge(roots), BARK), node("cobble_slabs", merge(slabs), STONE)])
if __name__ == "__main__": print(compile_glb(root_node, out("environment", "env_mossy_forest_cliff_modular"), 512))
