from kingdom_lib import *
r = np.random.RandomState(5); L, Wd = 4.4, 2.0
def wheel(x, z, R=.64, y=.64):
    sg = 1 if x > 0 else -1; rim = torus(R - .03, .04, (0, 0, 0), rot=(0, 0, 90), seg=56, sides=12); fel = torus(R - .1, .055, (0, 0, 0), rot=(0, 0, 90), seg=48, sides=10, scale=(1.5, 1, 1))
    hub = cyl_tri(.13, .3, (0, 0, 0), 2, 20, rot=(0, 0, 90)); parts = [hub]; sp = []; nails = []
    for k in range(12):
        a = k * np.pi / 6; sp.append(tube((0, np.cos(a) * .1, np.sin(a) * .1), (0, np.cos(a) * (R - .1), np.sin(a) * (R - .1)), .032, 8, r2=.024))
    for k in range(30): a = k * 2 * np.pi / 30; nails.append(box_tri((.04, .05, .05), (sg * .045, np.cos(a) * (R - .005), np.sin(a) * (R - .005)), (np.degrees(a), 0, 0), 3))
    return [m.tf(pos=(x, y, z)) for m in (rim, merge(nails), fel, merge(sp), hub)]
wh = [wheel(sx * 1.2, z) for sx in (-1, 1) for z in (-1.5, 1.4)]
ax = [tube((-1.4, .64, z), (1.4, .64, z), .07, 12) for z in (-1.5, 1.4)]
bed = [box_tri((Wd, .16, L), (0, .95, 0), d=.8), box_tri((Wd + .2, .14, .14), (0, .8, 1.4), d=.8), box_tri((Wd + .2, .14, .14), (0, .8, -1.5), d=.8)] + [box_tri((.14, .2, L + .1), (sx * (Wd / 2 - .1), .82, 0), d=.8) for sx in (-1, 1)]
boards = []
for sx in (-1, 1):
    for k in range(5): boards.append(box_tri((.05, .17, L - .02), (sx * (Wd / 2 + .02), 1.14 + k * .185, 0), d=.9, seg=2))
    for z in np.linspace(-L / 2 + .1, L / 2 - .1, 11): boards.append(box_tri((.1, 1.0, .1), (sx * (Wd / 2 + .06), 1.5, z), d=.9))
for k in range(5): boards.append(box_tri((Wd, .17, .05), (0, 1.14 + k * .185, -L / 2), d=.9, seg=2))
ribs, can = [], []
zs = np.linspace(-1.9, 1.0, 7); t = np.linspace(0, np.pi, 28)
for z in zs: ribs.append(spline_tube([(Wd / 2 * 1.02 * np.cos(a), 1.5 + 1.5 * np.sin(a), z) for a in np.linspace(0, np.pi, 9)], [.045] * 9, rings=36, sides=8, bark_disp=.01, cap=True))
rows = np.linspace(-2.05, 1.15, 49); P = np.zeros((len(rows), len(t), 3))
for i, z in enumerate(rows):
    k = np.argmin(np.abs(zs - z)); sag = .035 * np.sin(np.pi * ((z - zs[max(0, k - (1 if z < zs[k] else 0))]) / (zs[1] - zs[0]) % 1)) if True else 0
    for j, a in enumerate(t): P[i, j] = ((Wd / 2 * 1.06 - sag) * np.cos(a), 1.5 + (1.55 - sag) * np.sin(a), z)
canvas = scale_uv(grid(P, closed_u=False, flip=True), 2.0, 2.5)
bench = [box_tri((1.7, .12, .55), (0, 1.55, 1.95), d=1), box_tri((1.7, .5, .08), (0, 1.9, 1.7), d=1), box_tri((1.9, .08, .55), (0, 1.0, 2.35), (-20, 0, 0), 1), box_tri((1.7, .1, .5), (0, 1.63, 1.95), d=2)]
tongue = [tube((0, .9, 2.2), (0, .95, 4.4), .06, 10), tube((-.5, .95, 4.3), (.5, .95, 4.3), .05, 10)]; braces = [tube((sx * .8, .85, 1.5), (0, .9, 2.8), .035, 8) for sx in (-1, 1)]
def barrel(x, z, h=.9, rr=.38):
    prof = [(rr * .8, 0), (rr * .95, h * .2), (rr, h * .5), (rr * .95, h * .8), (rr * .8, h)]; b = lathe(prof, 28, True, (x, 1.03, z)); hoops = [torus(rr * f + .01, .018, (x, 1.03 + h * y, z), seg=28, sides=6) for f, y in ((.84, .08), (.97, .3), (.97, .7), (.84, .92))]
    return b, hoops
bars = [barrel(-.55, -1.5), barrel(.5, -1.4), barrel(0, -.55, .8, .34)]
crates = [box_tri((.7, .5, .6), (-.5, 1.3, -.4), (0, 15, 0), 1.5, 2), box_tri((.6, .45, .55), (.55, 1.28, -.15), (0, -10, 0), 1.5, 2), box_tri((.55, .4, .5), (.5, 1.75, -.18), (0, 25, 0), 1.5, 2)]
slats = [box_tri((.74, .06, .64), (-.5, 1.3 + dy, -.4), (0, 15, 0), 2) for dy in (-.2, .2)]
sacks = [ell((x, 1.25 + h, z), (.3, .24 + h, .25), 12, 14, 1.5) for x, z, h in ((-.2, .6, .05), (.35, .55, .1), (-.55, .2, .0))]
lantern = [box_tri((.18, .26, .18), (.85, 2.15, 1.9), d=1), tube((.85, 2.28, 1.9), (.85, 2.6, 1.9), .015, 6)]; lframe = [box_tri((.22, .04, .22), (.85, 2.3, 1.9), d=2), box_tri((.22, .04, .22), (.85, 2.0, 1.9), d=2)]
root = node("veh_merchant_covered_wagon", None, None, [node("oak_chassis_rails", merge(bed + boards + bench[:2] + bench[2:3] + tongue + braces + crates + slats + [bars[0][0], bars[1][0], bars[2][0]] + [m for b in bars for m in b[1]][:0] + ax + [m for w in wh for m in (w[2], w[3], w[4])]), OAKP),
    node("canopy_ribs", merge(ribs), BEAM), node("iron_rims_hoops", merge([m for w in wh for m in w[:2]] + [h for b in bars for h in b[1]] + lframe), DARKSTEEL), node("canvas_canopy", canvas, CANVAS), node("cargo_sacks", merge(sacks + [bench[3]]), CANVAS if False else LEATHERS), node("lit_lantern", merge(lantern[:1]), GLASSLIT)])
if __name__ == "__main__": print(compile_glb(root, out("vehicles", "veh_merchant_covered_wagon"), 512))
