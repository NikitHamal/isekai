from common import *
import numpy as np
BLADE = Material("aether_steel", "hammered_metal", (.8, .85, .9), (.55, .62, .72), rough=.25, metal=1.0, scale=3, bump=.8, seed=21)
LEATHER = Material("grip_leather", "woven_cloth", (.3, .17, .1), (.15, .08, .05), rough=.8, scale=10, bump=3, seed=22)
RUNE = Material("rune_glow", "runic_glow", (.1, .6, .8), (.05, .3, .5), rough=.3, emissive=(.2, .9, 1.0), scale=5, seed=23)
n = 60; t = np.linspace(0, 1, n)[:, None]; hw = (.075 * (1 - t**3 * .7)); hw[-4:] *= np.linspace(1, .05, 4)[:, None]
ph = np.linspace(0, 2*np.pi, 25)[None]   # lens-shaped cross-section with fuller groove
x = hw * np.cos(ph); z = .018 * np.sin(ph) * (1 - .35 * np.exp(-((np.cos(ph)) / .35) ** 2) * (np.abs(np.sin(ph)) > .5)); y = (0 + t * 1.05) + 0 * ph
z = np.broadcast_to(z, x.shape)
blade = grid(np.stack([x, y, z], -1), uscale=1, vscale=4, cap=True)
rune = merge([box((.02, .05 + .02 * (i % 3), .004), (0, .2 + .1 * i, .016), seg=2) for i in range(7)])
guard = merge([spline_tube([(0, 0, 0), (s * .12, .005, 0), (s * .25, .06, 0), (s * .33, .14, 0)], [.035, .03, .022, .01], rings=14, sides=12, bark_disp=0) for s in (-1, 1)] + [box((.1, .06, .05), (0, .01, 0), seg=4)])
wings = merge([box((.05, .015, .02), (s * (.15 + .06 * k), .045 + .03 * k * k + .02, 0), (0, 0, s * (-20 - 10 * k)), seg=3) for s in (-1, 1) for k in range(4)])
grip = spline_tube([(0, -.05, 0), (0, -.17, 0), (0, -.3, 0)], [.024, .028, .024], twist=18, rings=36, sides=14, bark_disp=.1, seed=3)
wrap = merge([torus(.03, .006, (0, -.06 - .02 * i, 0), rot=(0, 0, 0), seg=18, sides=6) for i in range(11)])
pommel = merge([sphere(.045, (0, -.34, 0), (1, 1.1, 1), 16, 20), torus(.04, .008, (0, -.34, 0), seg=20, sides=8)])
root_node = node("wpn_aetherblade_longsword", None, None, [node("blade", blade, BLADE, pos=(0, .035, 0)), node("rune_inlay", rune, RUNE), node("crossguard", guard, GOLD), node("guard_wings", wings, GOLD),
    node("grip", grip, LEATHER), node("grip_wrap", wrap, ROPE), node("pommel", pommel, GOLD)])
if __name__ == "__main__": print(compile_glb(root_node, out("weapons", "wpn_aetherblade_longsword"), 256))
