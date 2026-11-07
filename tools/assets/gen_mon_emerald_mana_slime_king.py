from common import *
import numpy as np
body = sdf_sculpt([('ellipsoid', (0, .3, 0), (.7, .3, .7)), ('sphere', (0, .6, 0), .5), ('sphere', (0, .98, 0), .3), ('sphere', (0, 1.26, 0), .13)], resolution=140, smooth_k=.32, pad=.2)
body = subdivide(body, 1, .2) if body.tris < 5200 else body
core = merge([sphere(.2, (0, .6, .05), rings=24, sides=32), sphere(.27, (0, .6, .05), (1, 1, 1), 16, 24)])
crystals = merge([sphere(.07, (np.cos(a) * .3, .45 + .25 * np.sin(2 * a + 1), np.sin(a) * .3), (.6, 1.9, .6), 4, 6).tf(rot=(20 * k, 30 * k, 15)) for k, a in enumerate(np.linspace(0, 6.28, 7, endpoint=False))])
ccore = merge([sphere(.075, (np.cos(a) * .6, .55 + .3 * np.sin(2 * a), np.sin(a) * .6), (.6, 1.8, .6), 5, 6) for a in np.linspace(.4, 6.28, 5, endpoint=False)])
crown = lathe([(.17, 0), (.2, .03), (.215, .1), (.19, .17), (.17, .12), (.15, .04), (.17, 0)], 40, bevel=True)
spikes = merge([cylinder(.03, .12, (np.cos(a) * .19, .2, np.sin(a) * .19), r2=.003, sides=10, rings=3) for a in np.linspace(0, 6.28, 6, endpoint=False)] + [sphere(.026, (np.cos(a) * .19, .27, np.sin(a) * .19), rings=8, sides=10) for a in np.linspace(0, 6.28, 6, endpoint=False)])
gems = merge([sphere(.03, (np.cos(a) * .213, .09, np.sin(a) * .213), (1, 1.2, .8), 8, 10) for a in np.linspace(.3, 6.28, 3, endpoint=False)])
tilt = dict(pos=(.05, 1.3, .02), rot=(0, 0, -14))
eyes = merge([sphere(.045, (s * .15, .76, .5), (1, 1.4, .8), 12, 16) for s in (-1, 1)]); glints = merge([sphere(.014, (s * .15 + .012, .79, .545), rings=6, sides=8) for s in (-1, 1)])
mouth = spline_tube([(-.12, .64, .49), (-.05, .6, .53), (.05, .6, .53), (.12, .64, .49)], [.011, .013, .013, .011], rings=14, sides=6, bark_disp=0)
root_node = node("mon_emerald_mana_slime_king", None, None, [node("gelatinous_body", body, SLIMEGEL), node("mana_core", core, MANA), node("floating_crystals", merge([crystals, ccore]), CRYSTAL),
    node("royal_crown", crown, GOLD, [node("crown_spikes", spikes, GOLD), node("crown_gems", gems, RUBY)], **tilt), node("eyes", eyes, IRON), node("eye_glints", glints, LUMEN), node("smile", mouth, IRON)])
if __name__ == "__main__": print(compile_glb(root_node, out("monsters", "mon_emerald_mana_slime_king"), 256))
