from kingdom_lib import *
r = np.random.RandomState(51)
def limb(pts, rad, sides=18): return merge([tube(pts[i], pts[i + 1], rad[i], sides, 3, rad[i + 1]) for i in range(len(pts) - 1)])
body = [ell((0, .98, -.1), (.3, .34, .72), 28, 40), ell((0, 1.08, .55), (.34, .4, .42), 26, 36), ell((0, .88, -.65), (.26, .27, .38), 22, 30)]
neck = [limb([(0, 1.12, .8), (0, 1.3, 1.05), (0, 1.34, 1.2)], [.26, .2, .17], 22)]
head = [ell((0, 1.32, 1.32), (.17, .17, .22), 22, 32), ell((0, 1.24, 1.58), (.1, .09, .2), 18, 26), ell((0, 1.2, 1.5), (.09, .05, .17), 12, 18)]
ears = [cyl_tri(.07, .24, (s * .11, 1.56, 1.25), 4, 10, r2=.006, rot=(-10, 0, -s * 14)) for s in (-1, 1)]
teeth = [cyl_tri(.012, .06, (dx, 1.16, 1.62 + abs(dx) * -.3), 3, 6, r2=.002, rot=(180, 0, 0)) for dx in np.linspace(-.06, .06, 6)] + [cyl_tri(.012, .05, (dx, 1.19, 1.62), 3, 6, r2=.002) for dx in np.linspace(-.05, .05, 5)] + [ell((0, 1.28, 1.76), (.03, .02, .02), 8, 10)]
eyes = [ell((s * .1, 1.37, 1.46), (.025, .018, .02), 8, 10) for s in (-1, 1)]
legs, paws = [], []
for s in (-1, 1):
    for z, front in ((.62, True), (-.62, False)):
        hip = (s * .22, .95, z); knee = (s * .24, .55, z + (.1 if front else -.12)); ank = (s * .24, .22, z + (.02 if front else -.2)); paw = (s * .24, .05, z + .12)
        legs += [limb([hip, knee], [.13 if front else .15, .08], 18), limb([knee, ank], [.075, .05], 14), ell(knee, (.085, .085, .085), 10, 14)]; paws += [ell(paw, (.075, .05, .14), 12, 16)] + [cyl_tri(.01, .06, (s * .24 + dx, .03, z + .26), 3, 6, r2=.002, rot=(90, 0, 0)) for dx in (-.04, 0, .04)]
tail = [spline_tube([(0, 1.0, -.95), (0, .95, -1.3), (0, .7, -1.6), (0, .4, -1.75)], [.08, .1, .08, .01], rings=24, sides=12, bark_disp=.02)]
fur = []
for i in range(190):   # ragged shadow-fur tufts along spine, mane, flanks
    t = r.rand(); z = -1.0 + t * 2.3; th = r.rand() * np.pi * 2; rad = .27 if z < .8 else .33
    p = np.array([np.cos(th) * rad * .9, .98 + np.sin(th) * (.34 if z < .8 else .42) + (.0 if z < .8 else .1) + (.28 if 0.7 < z < 1.3 else 0) * (np.sin(th) > 0), z]); d = np.array([np.cos(th) * .5, abs(np.sin(th)) * .8 + .2, -.7])
    if z > 1.0: p = np.array([np.cos(th) * .2, 1.35 + np.sin(th) * .2, z - .15]); d = np.array([np.cos(th) * .4, .7, -.8])
    fur.append(tube(p, p + d / np.linalg.norm(d) * (.12 + .15 * r.rand()), .028, 5, 3, .003))
root = node("mon_shadow_direwolf_alpha", None, None, [node("shadow_fur_body", merge(body + neck + head + ears + legs + tail + fur), FURM), node("paws_claws_fangs", merge(paws + teeth), BONEM), node("glowing_violet_eyes", merge(eyes), SHADOWEYE)])
if __name__ == "__main__": print(compile_glb(root, out("monsters", "mon_shadow_direwolf_alpha"), 512))
