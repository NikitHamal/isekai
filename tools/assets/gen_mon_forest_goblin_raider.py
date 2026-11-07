from common import *
import numpy as np
body = sdf_sculpt([('ellipsoid', (0, .78, .02), (.27, .3, .21)), ('ellipsoid', (0, .98, .12), (.3, .2, .22)), ('ellipsoid', (0, .6, -.04), (.21, .18, .19)),
    ('sphere', (0, 1.17, .3), .17), ('ellipsoid', (0, 1.08, .38), (.1, .08, .12)), ('capsule', (0, 1.1, .2), (0, .98, .08), .11),
    ('capsule', (-.3, 1.02, .06), (-.46, .74, .16), .075), ('capsule', (-.46, .74, .16), (-.4, .46, .32), .06), ('sphere', (-.4, .43, .35), .075),
    ('capsule', (.3, 1.02, .06), (.5, .78, .12), .075), ('capsule', (.5, .78, .12), (.52, .52, .3), .06), ('sphere', (.52, .49, .33), .075),
    ('capsule', (-.14, .55, 0), (-.2, .3, .1), .095), ('capsule', (-.2, .3, .1), (-.16, .08, -.02), .065), ('ellipsoid', (-.16, .04, .06), (.07, .045, .13)),
    ('capsule', (.14, .55, 0), (.22, .3, .1), .095), ('capsule', (.22, .3, .1), (.17, .08, -.02), .065), ('ellipsoid', (.17, .04, .06), (.07, .045, .13)),
    ('ellipsoid', (0, 1.14, .47), (.06, .05, .05)), ('-', ('sphere', (0, 1.08, .48), .045))], resolution=150, smooth_k=.09, pad=.1)
body = subdivide(body, 1, .3) if body.tris < 9000 else body
def ear(sg):  # bat ear: long flat blade swept up/out + small inner fold, built at origin then placed on the skull
    e = merge([sphere(.06, (0, .0, 0), (.28, 1.8, .9), 12, 16).tf(pos=(0, .14, 0)), sphere(.035, (0, 0, 0), (.2, 1.5, .5), 8, 12).tf(pos=(0, .15, .015))])
    return e.tf(rot=(-10, 0, -sg * 62)).tf(pos=(sg * .15, 1.26, .27))
ears = merge([ear(-1), ear(1)])
eyes = merge([sphere(.026, (s * .075, 1.22, .45), (1, .8, .6), 10, 12) for s in (-1, 1)])
teeth = merge([cylinder(.008, .035, (x, 1.075, .495), r2=.001, sides=6, rings=1, rot=(0, 0, 180)) for x in (-.03, -.012, .012, .03)])
pads = merge([sphere(.13, (s * .31, 1.1, .07), (1, .5, 1.1), 14, 18) for s in (-1, 1)] + [torus(.08, .012, (s * .39, .9, .12), rot=(0, 0, 60 * s), seg=16, sides=6) for s in (-1, 1)] + [box((.05, .04, .15), (s * .31, 1.12, .07), seg=2) for s in (-1, 1)])
straps = spline_tube([(-.2, 1.12, .17), (0, .93, .26), (.22, .78, .2)], [.025, .03, .025], rings=18, sides=8, bark_disp=0, flat=.4)
cloth = folded([(.2, .62), (.23, .5), (.26, .36), (.25, .3)], 7, .09, 48, .85)
blade = grid(np.stack([np.array([[(.04 + .05 * t + (.012 if (k % 6 < 2) else 0)) * s for s in np.linspace(-1, 1, 5)] for k, t in enumerate(np.linspace(0, 1, 36))]), np.tile(np.linspace(.12, .42, 36)[:, None], (1, 5)), np.tile(np.array([-.008, -.004, .0, .004, .008]) * 1, (36, 1)) * 0 + np.array([-.01, -.012, .0, .012, .01])], -1), closed_u=False, cap=False)
cleaver = merge([blade.tf(pos=(.52, .5, .33), rot=(90, 0, 15)), cylinder(.02, .16, (.52, .5, .33), sides=12, rings=2, rot=(90, 0, 15)), torus(.026, .007, (.52, .5, .29), rot=(90, 0, 15), seg=12, sides=5)])
buckler = merge([sphere(.2, (-.4, .5, .5), (1, 1, .35), 20, 28).tf(pos=(0, 0, 0)), torus(.2, .02, (-.4, .5, .46), rot=(90, 0, 0), seg=36, sides=8)] + [cylinder(.016, .1, (-.4 + .13 * np.cos(a), .5 + .13 * np.sin(a), .55), r2=.001, sides=8, rings=2, rot=(90, 0, 0)) for a in np.linspace(0, 6.28, 8, endpoint=False)])
root_node = node("mon_forest_goblin_raider", None, None, [node("sculpted_body", body, GOBSKIN), node("bat_ears", ears, GOBSKIN), node("amber_eyes", eyes, AMBEREYE), node("fangs", teeth, BEIGE),
    node("shoulder_pads", pads, LEATHER), node("scavenged_strap", straps, LEATHER), node("loincloth", cloth, LEATHER), node("cleaver_attach", None, pos=(.52, .5, .33)),
    node("notched_iron_cleaver", cleaver, IRON), node("spiked_wood_buckler", buckler, OAK)])
if __name__ == "__main__": print(compile_glb(root_node, out("monsters", "mon_forest_goblin_raider"), 256))
