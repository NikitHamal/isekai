from kingdom_lib import *
r = np.random.RandomState(41)
def limb(pts, rad, sides=22): return merge([tube(pts[i], pts[i + 1], rad[i], sides, 3, rad[i + 1]) for i in range(len(pts) - 1)])
skin, iron, bone, leather = [], [], [], []
skin += [ell((0, 1.95, 0), (.5, .58, .34), 30, 44), ell((0, 1.25, .04), (.4, .3, .3), 20, 32), ell((0, 2.25, .1), (.5, .22, .3), 20, 32)]   # barrel chest, gut, shoulders hump
for s in (-1, 1):
    skin += [limb([(s * .3, 1.3, 0), (s * .3, .72, .05), (s * .32, .16, 0)], [.2, .15, .11], 24), ell((s * .32, .07, .14), (.14, .08, .26), 14, 22), ell((s * .3, .72, .1), (.16, .16, .16), 12, 18)]
    skin += [limb([(s * .66, 2.3, 0), (s * .86, 1.78, .1), (s * .82, 1.3, .3)], [.2, .17, .13], 24), ell((s * .86, 1.78, .1), (.18, .18, .18), 14, 20), ell((s * .8, 1.24, .34), (.14, .14, .13), 14, 20)]
    iron += [ell((s * .74, 2.36, 0), (.3, .13, .3), 18, 30, 1, (0, 0, -s * 22))] + [cyl_tri(.05, .3 + .06 * k, (s * (.62 + .1 * k + .03 * dx), 2.5 + .08 * k, dz * .1), 3, 8, r2=.004, rot=(0, 0, -s * 25)) for k in range(3) for dx, dz in ((0, 0), (1, 1), (-1, -1))]
    iron += [limb([(s * .86, 1.74, .1), (s * .82, 1.3, .3)], [.19, .15], 20)] if False else []
    leather += [cyl_tri(.15, .26, (s * .83, 1.42, .28), 3, 20, r2=.13), torus(.2, .03, (s * .84, 1.7, .1), seg=24, sides=8)]
# head: heavy jaw, tusks, glowing eyes, horned skull helm
head = [ell((0, 2.62, .12), (.24, .27, .26), 24, 36), ell((0, 2.46, .26), (.2, .13, .18), 18, 28), ell((0, 2.56, .36), (.07, .05, .06), 10, 14)]
tusks = [spline_tube([(s * .12, 2.43, .38), (s * .17, 2.52, .46), (s * .15, 2.7, .48)], [.035, .025, .004], rings=14, sides=8, bark_disp=0) for s in (-1, 1)]
eyes = [ell((s * .09, 2.65, .36), (.03, .02, .02), 8, 10) for s in (-1, 1)]
helm = [ell((0, 2.72, .08), (.265, .21, .28), 26, 40)] + [ell((s * .12, 2.66, .34), (.07, .035, .03), 8, 10) for s in (-1, 1)]
horns = [spline_tube([(s * .2, 2.82, .06), (s * .42, 2.88, .04), (s * .55, 3.12, .0), (s * .52, 3.34, .05)], [.07, .06, .04, .005], rings=30, sides=12, bark_disp=.015) for s in (-1, 1)]
teeth = [cyl_tri(.014, .06, (dx, 2.42, .42), 3, 6, r2=.003, rot=(180, 0, 0)) for dx in np.linspace(-.1, .1, 7)]
# belt of skulls, loincloth, armour plates
belt = [torus(.38, .05, (0, 1.2, .03), seg=40, sides=10, scale=(1.05, 1, .8)), folded([(.4, 1.2), (.42, .9), (.44, .7)], 9, .08, 48, .6)] + [ell((x, 1.15, .32), (.07, .08, .06), 10, 14) for x in (-.25, .0, .25)]
plates = [ell((0, 2.0, .12), (.46, .42, .27), 22, 36)]
# greataxe: ash haft, iron double-crescent head, spike
G = np.array([.82, 1.3, .38]); haft = [tube(G + [0, -.6, 0], G + [0, 1.5, 0], .045, 14)]; head_a = []
for s in (-1, 1):
    head_a.append(poly_prism([(0, 0), (.04, .0), (.42, .12), (.55, .0), (.5, -.3), (.35, -.38), (.0, -.2)] if s > 0 else [(0, 0), (-.04, 0), (-.42, .12), (-.55, 0), (-.5, -.3), (-.35, -.38), (0, -.2)][::-1] if False else [(0, 0), (-.04, 0), (-.0, -.2), (-.35, -.38), (-.5, -.3), (-.55, 0), (-.42, .12)], .04, G + [0, 1.3, 0], d=2))
spike = [cyl_tri(.05, .3, G + [0, 1.65, 0], 3, 10, r2=.004), ell(G + [0, -.62, 0], (.06, .06, .06), 8, 10)]
hand = [ell(G + [0, 0, 0], (.12, .1, .1), 12, 16)]
root = node("mon_orc_warlord_berserker", None, None, [node("orc_hide_body", merge(skin + head + hand), ORCSKIN), node("iron_pauldrons_spikes", merge(iron + plates), DARKSTEEL), node("bone_horns_tusks", merge(helm + horns + tusks + teeth), BONEM),
    node("leather_belt_bracers", merge(belt[:2] + leather), LEATHERS), node("skull_belt", merge(belt[2:]), BONEM), node("glowing_eyes", merge(eyes), RUBY), node("greataxe_haft", merge(haft + spike[1:]), BEAM), node("greataxe_blades", merge(head_a + spike[:1]), DAMASK)])
if __name__ == "__main__": print(compile_glb(root, out("monsters", "mon_orc_warlord_berserker"), 512))
