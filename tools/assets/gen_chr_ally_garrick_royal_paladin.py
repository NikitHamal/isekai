from kingdom_lib import *
r = np.random.RandomState(31)
def limb(pts, rad, sides=20): return merge([tube(pts[i], pts[i + 1], rad[i], sides, 3, rad[i + 1]) for i in range(len(pts) - 1)])
steel, cloth, leather, gold, under = [], [], [], [], []
for s in (-1, 1):  # fluted plate greaves/cuisses, sabatons
    steel += [limb([(s * .12, 1.0, 0), (s * .125, .56, .03)], [.115, .09], 24), limb([(s * .125, .56, .03), (s * .115, .12, 0)], [.088, .065], 24), ell((s * .125, .55, .06), (.085, .09, .07), 14, 22), ell((s * .115, .05, .09), (.075, .05, .17), 14, 22)]
    steel += [tube((s * .12 + dx, .98, .09), (s * .125 + dx * .8, .6, .11), .008, 6) for dx in (-.04, 0, .04)]
    under.append(limb([(s * .12, 1.05, 0), (s * .12, .1, 0)], [.085, .06], 14))
    steel += [limb([(s * .31, 1.7, 0), (s * .39, 1.38, .06)], [.08, .068], 22), limb([(s * .39, 1.38, .06), (s * .4, 1.1, .2)], [.066, .052], 22), ell((s * .39, 1.38, .06), (.075, .075, .075), 12, 18), ell((s * .4, 1.08, .21), (.058, .065, .065), 12, 18)]
    steel += [ell((s * (.33 + .02 * k), 1.78 - .06 * k, 0), (.12 + .01 * k, .04, .15 + .01 * k), 14, 26, 1, (0, 0, -s * (20 + 8 * k))) for k in range(4)]
    gold += [cyl_tri(.014, .1, (s * (.36 + .02 * k) + s * .02, 1.86 - .06 * k, 0), 3, 8, r2=.001) for k in range(3)] + [ell((s * .34, 1.88, 0), (.055, .06, .05), 10, 14)]   # lion-crest pauldron studs/heads
steel += [ell((0, 1.5, .01), (.27, .28, .17), 30, 44), ell((0, 1.22, .02), (.22, .1, .15), 16, 30), ell((0, 1.76, 0), (.13, .05, .11), 14, 24)] + [tube((dx, 1.7, .15 - abs(dx) * .3), (dx * .9, 1.28, .17 - abs(dx) * .25), .009, 6) for dx in np.linspace(-.17, .17, 7)]
under.append(ell((0, 1.45, 0), (.24, .32, .15), 20, 30))
cloth.append(folded([(.27, 1.1), (.3, .85), (.32, .6), (.31, .4)], 13, .07, 56, .75)); cloth.append(box_tri((.2, .6, .02), (0, 1.15, .2), d=2, seg=3))
leather += [torus(.24, .035, (0, 1.12, 0), seg=36, sides=8, scale=(1, 1, .72))]; gold += [box_tri((.08, .07, .03), (0, 1.12, .18), d=5), ell((0, 1.82, .02), (.02, .02, .02), 8, 8)]
# helm: closed visored great-helm, crimson plume
helm = [ell((0, 1.92, 0), (.115, .14, .125), 28, 40), cyl_tri(.11, .1, (0, 1.78, 0), 4, 28, r2=.1)]; visor = [box_tri((.17, .014, .02), (0, 1.94, .115), d=8)] + [box_tri((.006, .06, .02), (dx, 1.88, .118), d=8) for dx in np.linspace(-.05, .05, 6)]
crest = [ell((0, 2.04, -.02), (.02, .08, .15), 10, 18)]; plume = [spline_tube([(0, 2.1, -.1), (0, 2.25, -.18), (0, 2.12, -.34), (0, 1.9, -.4)], [.035, .05, .045, .015], rings=24, sides=10, bark_disp=.01)]
neck = [tube((0, 1.7, 0), (0, 1.8, 0), .06, 12)]
cape = []
nr, nc = 32, 32; P = np.zeros((nr, nc, 3))
for i in range(nr):
    v = i / (nr - 1)
    for j in range(nc): u = j / (nc - 1) * 2 - 1; P[i, j] = (u * (.26 + .26 * v), 1.78 - v * 1.45, -.18 - .24 * v ** 1.3 + .05 * v * np.sin(u * 3 * np.pi))
capeg = grid(P, closed_u=False)
# tower shield (left arm) with lion boss + broadsword (right hand)
sh = poly_prism([(-.38, 1.7), (.38, 1.7), (.4, 1.2), (.25, .6), (0, .3), (-.25, .6), (-.4, 1.2)], .07, (.5, 0, .3), d=1.5, rot=(0, -25, 0)); rim = [tube((.5, 1.7, .3), (.5, .3, .3), .001, 4)]
boss = [ell((.5 + .0, 1.2, .38), (.1, .1, .05), 14, 20, 1, (0, -25, 0)), ell((.5, 1.45, .36), (.06, .08, .03), 10, 14, 1, (0, -25, 0)), ell((.47, 1.0, .37), (.1, .05, .03), 10, 14)]
G = np.array([-.4, 1.1, .22]); sword = [tube(G + [0, -.13, 0], G + [0, .12, 0], .02, 12), box_tri((.36, .035, .05), G + [0, .14, 0], d=3), ell(G + [0, -.15, 0], (.035, .035, .035), 12, 14)]
blade = poly_prism([(-.04, 0), (.04, 0), (.036, 1.0), (0, 1.12), (-.036, 1.0)], .016, G + [0, .16, 0], d=2.2)
root = node("chr_ally_garrick_royal_paladin", None, None, [node("fluted_plate_armor", merge(steel + under[:0] + [sh]), DAMASK), node("padded_underlayer", merge(under), GAMBE), node("crimson_surcoat", merge(cloth), CRIMSONCLOTH), node("royal_cape", capeg, CLOAKR),
    node("belt_leather", merge(leather), LEATHERS), node("great_helm", merge(helm + neck + crest + visor), DAMASK), node("crimson_plume", merge(plume), CRIMSONCLOTH), node("lion_gold_crests", merge(gold + boss), GOLDM), node("broadsword_hilt", merge(sword), GOLDM), node("broadsword_blade", blade, DAMASK)])
if __name__ == "__main__": print(compile_glb(root, out("characters", "chr_ally_garrick_royal_paladin"), 512))
