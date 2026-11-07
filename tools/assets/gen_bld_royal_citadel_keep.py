from kingdom_lib import *
GH, GW, GD, R = 18.0, 9.0, 8.0, 3.5      # gatehouse: x +-9, z +-8, passage half-width 3.5 (arch springs y=4.3)
hz = GD
# ---- gatehouse masonry: two piers, spandrel slabs shaping an arched passage, upper block ----
core = [box_tri((GW - R, GH, 2 * GD), ((GW + R) / 2 * s, GH / 2, 0), d=.28) for s in (-1, 1)] + [box_tri((2 * R, GH - 7.8, 2 * GD), (0, 7.8 + (GH - 7.8) / 2, 0), d=.28)]
spand = []
for y in np.arange(4.3, 7.8, .35):
    ix = np.sqrt(max(R * R - (y + .175 - 4.3) ** 2, 0)); 
    if R - ix > .02: spand += [box_tri((R - ix, .35, 2 * GD), (s * (ix + (R - ix) / 2), y + .175, 0), d=.5) for s in (-1, 1)]
rel = []
for z, sd in ((hz, 1), (-hz - .14, 2)):
    rel += [block_wall(-GW, -R, 0, GH, z, .14, .4, .9, sd, holes=[(-8.3, -7.1, 9.5, 12.6), (-8.3, -7.1, 14.0, 16.2)]), block_wall(R, GW, 0, GH, z, .14, .4, .9, sd + 10, holes=[(7.1, 8.3, 9.5, 12.6), (7.1, 8.3, 14.0, 16.2)]),
            block_wall(-R, R, 8.2, GH, z, .14, .4, .9, sd + 20, holes=[(-.9, .9, 11, 13.5)])]
rel += [block_wall(-GD, GD, 0, GH, s * GW + (0 if s > 0 else -.14), .14, .4, .9, 40 + s, axis=1) for s in (-1, 1)]
arch = [arch_opening(0, 0, 2 * R, 4.3, hz + .02, .5, n=21), arch_opening(0, 0, 2 * R, 4.3, -hz - .02, .5, n=21)]
# raised iron portcullis (hangs inside the arch head) + gate torches
bars = []
for x in np.arange(-3.1, 3.2, .45):
    yt = 4.3 + np.sqrt(max(R * R - x * x, 0)) - .1; bars.append(tube((x, yt - 2.0, hz - 1.2), (x, yt, hz - 1.2), .06, 8)); bars.append(cyl_tri(.07, .25, (x, yt - 2.1, hz - 1.2), 2, 6, r2=.005, rot=(0, 0, 180)))
for y in (5.2, 6.4, 7.2): bars.append(tube((-2.6, y, hz - 1.2), (2.6, y, hz - 1.2), .05, 8))
torch = [tube((s * 4.9, 3.0, hz + .5), (s * 4.9, 3.9, hz + .5), .06, 8) for s in (-1, 1)]; flame = [ell((s * 4.9, 4.1, hz + .5), (.2, .3, .2), 8, 10) for s in (-1, 1)]
# ---- crenellated parapets + curtain walls + towers ----
cren = [crenellations(-GW, GW, GH, z, .6, .9, 1.0, .7, 0, 60 + i) for i, z in enumerate((hz - .3, -hz + .3))] + [crenellations(-GD + .6, GD - .6, GH, s * (GW - .3), .6, .9, 1.0, .7, 1, 70) for s in (-1, 1)]
walk = [box_tri((2 * GW - .2, .5, 2 * GD - .2), (0, GH + .1, 0), d=.5)]
WH = 11.0; walls = []; wcr = []
for s in (-1, 1):
    x0, x1 = sorted((s * GW, s * 16.5)); walls += [box_tri((x1 - x0, WH, 3.0), ((x0 + x1) / 2, WH / 2, 0), d=.28), block_wall(x0, x1, 0, WH, 1.5, .14, .4, .9, 80 + s), block_wall(x0, x1, 0, WH, -1.64, .14, .4, .9, 90 + s)]
    wcr += [crenellations(x0, x1, WH, z, .6, .9, .9, .7, 0, 100 + s) for z in (1.2, -1.2)] + [box_tri((x1 - x0, .4, 3.0), ((x0 + x1) / 2, WH + .1, 0), d=.5)]
    walls += [box_tri((1.8, WH + 1.5, 1.8), (s * 13.0, (WH + 1.5) / 2, 2.3), d=.5), box_tri((1.8, WH + 1.5, 1.8), (s * 13.0, (WH + 1.5) / 2, -2.3), d=.5)]
towers = [round_tower(4.0, 23.0, (s * 9.5, 0, 8.6), 110 + int(s)) for s in (-1, 1)] + [round_tower(4.0, 19.0, (s * 16.5, 0, 0), 120 + int(s)) for s in (-1, 1)]
# ---- windows, arrow slits, banners ----
glass = [box_tri((1.0, 2.2, .06), (s * 7.7, 11.1, hz + .12), d=1) for s in (-1, 1)] + [box_tri((1.0, 1.9, .06), (s * 7.7, 15.1, hz + .12), d=1) for s in (-1, 1)] + [box_tri((1.7, 2.3, .06), (0, 12.2, hz + .12), d=1)]
frames = [box_tri((w + .4, h + .4, .12), (x, y, hz + .08), d=.8) for x, y, w, h in [(-7.7, 11.1, 1.0, 2.2), (7.7, 11.1, 1.0, 2.2), (-7.7, 15.1, 1.0, 1.9), (7.7, 15.1, 1.0, 1.9), (0, 12.2, 1.7, 2.3)]]
slits = [box_tri((.22, 1.7, .3), (s * 5.2 + dx, 16.0 if dx == 0 else 11.0, hz + .1), d=1) for s in (-1, 1) for dx in (0,)] + [box_tri((.26, 1.6, .3), (s * 3.6, 6.0 + k * 2.4 + 5, hz + .1), d=1) for s in (-1, 1) for k in (0,)]
slitt = [box_tri((.28, 1.5, .3), (s * 9.5 + 4.05 * np.sin(a), 8 + k * 6, 8.6 + 4.05 * np.cos(a)), (0, np.degrees(a), 0), 1) for s in (-1, 1) for k in range(3) for a in (0.7, -0.7)]
ban = [box_tri((2.0, 7.0, .05), (s * 5.7 + (0 if True else 0), 13.2, hz + .35), d=.4) for s in (-1, 1)] + [box_tri((2.0, 7.0, .05), (s * 5.7, 13.2, -hz - .35), d=.4) for s in (-1, 1)]
trim = [box_tri((2.0, .25, .07), (s * 5.7, y, hz + .36), d=1.5) for s in (-1, 1) for y in (16.55, 9.95)] + [poly_prism([(-.8, 0), (.8, 0), (0, -1.1)], .06, (s * 5.7, 9.8, hz + .37), d=1.2) for s in (-1, 1)]
rods = [tube((s * 5.7 - 1.15, 16.8, hz + .3), (s * 5.7 + 1.15, 16.8, hz + .3), .05, 8) for s in (-1, 1)]
poles = [tube((s * 9.5, 23.8, 8.6), (s * 9.5, 26.0, 8.6), .07, 8) for s in (-1, 1)]; flags = [box_tri((1.5, .8, .04), (s * 9.5 + .8, 25.5, 8.6), d=.6) for s in (-1, 1)]
root = node("bld_royal_citadel_keep", None, None, [node("gatehouse_core", merge(core + spand + walk), CASTLE), node("ashlar_relief", merge(rel + walls), STONEF), node("arch_voussoirs", merge(arch), DARKSTONE),
    node("curtain_walls_towers", merge(towers + cren + wcr), STONEF), node("iron_portcullis", merge(bars + torch + slits + slitt + frames + rods + poles), DARKSTEEL), node("lit_windows_brazier", merge(glass + flame), GLASSLIT),
    node("royal_banners", merge(ban + flags), BANNER), node("gold_trim", merge(trim), GOLDM)])
if __name__ == "__main__": print(compile_glb(root, out("buildings", "bld_royal_citadel_keep"), 1024))
