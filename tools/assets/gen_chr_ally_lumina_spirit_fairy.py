from common import *
import numpy as np
core = merge([sphere(.1, (0, 0, 0), rings=28, sides=40), sphere(.135, (0, 0, 0), (1, 1.05, 1), 20, 28)])
head = sphere(.055, (0, .17, 0), (1, 1.05, 1), 16, 22); body = lathe([(.001, .08), (.05, .1), (.045, .0), (.075, -.12), (.11, -.22), (.001, -.26)], 28, pos=(0, 0, 0))
hair = merge([spline_tube([(a * .02, .2, -.02), (a * .06, .17, -.06), (a * .09, .08 - k * .05, -.07 - k * .01)], [.014, .011, .002], rings=10, sides=8, bark_disp=0) for k, a in enumerate([-1, -.5, .5, 1] * 2)])
limbs = merge([spline_tube([(s * .04, .06, 0), (s * .1, .0 - k * .03, .03), (s * .13, -.06 - k * .05, .06)], [.012, .01, .007], rings=10, sides=8, bark_disp=0) for s in (-1, 1) for k in (0, 1)])
eyes = merge([sphere(.009, (s * .02, .18, .05), (1, 1.4, .6), 6, 8) for s in (-1, 1)])
wings, veins = [], []
for s in (-1, 1):
    for (ang, L, W, z) in ((s * 35 if s > 0 else 180 - 35, .62, .2, 0), (s * 18 if s > 0 else 180 + 18, .8, .25, -.0), (s * -30 if s > 0 else 180 + 30, .46, .14, -.02), (s * -40 if s > 0 else 180 + 40, .36, .1, -.02)):
        r = np.array([s * .035, .06, -.03]); wings += [wing(r, ang, L, W), wing(r, ang, L, W, flip=True).tf(pos=(0, 0, .004))]
        a = np.radians(ang); d = np.array([np.cos(a), np.sin(a), 0]); p = np.array([-np.sin(a), np.cos(a), 0])
        for q in (-.5, -.2, 0, .25, .5):
            pts = [r + d * L * u + p * q * W * np.sin(np.pi * u ** .75) * 1.6 * (1 if u > .1 else 0) + np.array([0, 0, -.15 * u * u * L + .004]) for u in (0, .3, .6, .9)]
            veins.append(spline_tube(pts, [.004, .0035, .003, .0015], rings=12, sides=6, bark_disp=0))
halos = merge([torus(.28 + .08 * k, .007, (0, 0, 0), rot=(70 - 35 * k, 25 * k, 0), seg=64, sides=8) for k in range(3)] + [sphere(.016, (np.cos(t) * (.28 + .08 * k), 0, np.sin(t) * (.28 + .08 * k)), rings=8, sides=10).tf(rot=(70 - 35 * k, 25 * k, 0)) for k in range(3) for t in (0, 2.1, 4.2)])
root_node = node("chr_ally_lumina_spirit_fairy", None, None, [node("luminous_core", core, LUMEN), node("sylph_body", merge([head, body, limbs]), SKIN), node("eyes", eyes, LUMEN), node("hair_wisps", hair, LUMEN),
    node("wings", merge(wings), WINGM), node("wing_veins", merge(veins), VEIN), node("mana_halo_rings", halos, HALO)])
if __name__ == "__main__": print(compile_glb(root_node, out("characters", "chr_ally_lumina_spirit_fairy"), 256))
